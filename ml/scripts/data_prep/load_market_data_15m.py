#!/usr/bin/env python3
"""
load_market_data_15m.py — Transform final_data CSVs → ml.market_data_15m in Postgres.

Parallelised: uses all available CPU cores (capped at 28).
Each worker reads one CSV, engineers features, and COPYs directly into Postgres.
COPY is ~10x faster than INSERT for bulk loads.

Does NOT touch ml/data/final_data/ — read-only on the CSVs.

Usage:
    python ml/scripts/data_prep/load_market_data_15m.py               # all symbols
    python ml/scripts/data_prep/load_market_data_15m.py --symbols AAPL,MSFT
    python ml/scripts/data_prep/load_market_data_15m.py --truncate    # wipe + reload
    python ml/scripts/data_prep/load_market_data_15m.py --workers 16  # override core count
"""
from __future__ import annotations

import argparse
import multiprocessing
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from dotenv import load_dotenv

# ── Paths ─────────────────────────────────────────────────────────────────────

ML_ROOT        = Path(__file__).resolve().parents[3] / "ml"
FINAL_DATA_DIR = ML_ROOT / "data" / "final_data"

# ── DB defaults ────────────────────────────────────────────────────────────────

DEFAULT_HOST  = "localhost"
DEFAULT_PORT  = 5432
DEFAULT_DB    = "app"
DEFAULT_USER  = "postgres"
DEFAULT_PASS  = "changethis"
TARGET_SCHEMA = "ml"
TARGET_TABLE  = "market_data_15m"

# ── Schema ─────────────────────────────────────────────────────────────────────

DDL = f"""
CREATE SCHEMA IF NOT EXISTS {TARGET_SCHEMA};

CREATE TABLE IF NOT EXISTS {TARGET_SCHEMA}.{TARGET_TABLE} (
    agg_id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol               TEXT        NOT NULL,
    trade_date           DATE        NOT NULL,
    window_ts            TIMESTAMPTZ NOT NULL,
    open                 NUMERIC(18,6),
    high                 NUMERIC(18,6),
    low                  NUMERIC(18,6),
    close                NUMERIC(18,6),
    volume               BIGINT,
    slot_count           INTEGER     NOT NULL DEFAULT 0,
    status               TEXT        NOT NULL DEFAULT 'final',
    created_at           TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lag_close_1          NUMERIC(18,6),
    lag_close_5          NUMERIC(18,6),
    lag_close_10         NUMERIC(18,6),
    close_diff_1         NUMERIC(18,6),
    close_diff_5         NUMERIC(18,6),
    pct_change_1         NUMERIC(18,6),
    pct_change_5         NUMERIC(18,6),
    log_return_1         NUMERIC(18,6),
    sma_close_5          NUMERIC(18,6),
    sma_close_10         NUMERIC(18,6),
    sma_close_20         NUMERIC(18,6),
    sma_volume_5         NUMERIC(18,6),
    day_of_week          SMALLINT,
    hour_of_day          SMALLINT,
    day_monday           SMALLINT    DEFAULT 0,
    day_tuesday          SMALLINT    DEFAULT 0,
    day_wednesday        SMALLINT    DEFAULT 0,
    day_thursday         SMALLINT    DEFAULT 0,
    day_friday           SMALLINT    DEFAULT 0,
    quarter_1            SMALLINT    DEFAULT 0,
    quarter_2            SMALLINT    DEFAULT 0,
    quarter_3            SMALLINT    DEFAULT 0,
    quarter_4            SMALLINT    DEFAULT 0,
    hour_early_morning   SMALLINT    DEFAULT 0,
    hour_mid_morning     SMALLINT    DEFAULT 0,
    hour_afternoon       SMALLINT    DEFAULT 0,
    hour_late_afternoon  SMALLINT    DEFAULT 0,
    previous_close       NUMERIC(18,6),
    overnight_gap_pct    NUMERIC(18,6),
    overnight_log_return NUMERIC(18,6),
    is_gap_up            SMALLINT,
    is_gap_down          SMALLINT,
    month_of_year        SMALLINT,
    UNIQUE (symbol, window_ts)
);

CREATE INDEX IF NOT EXISTS market_data_15m_symbol_window_ts_idx
    ON {TARGET_SCHEMA}.{TARGET_TABLE} (symbol, window_ts);
CREATE INDEX IF NOT EXISTS market_data_15m_window_ts_idx
    ON {TARGET_SCHEMA}.{TARGET_TABLE} (window_ts);
CREATE INDEX IF NOT EXISTS market_data_15m_status_idx
    ON {TARGET_SCHEMA}.{TARGET_TABLE} (status)
    WHERE status = 'provisional';
"""

COPY_COLS = [
    "symbol", "trade_date", "window_ts",
    "open", "high", "low", "close", "volume",
    "lag_close_1", "lag_close_5", "lag_close_10",
    "close_diff_1", "close_diff_5",
    "pct_change_1", "pct_change_5", "log_return_1",
    "sma_close_5", "sma_close_10", "sma_close_20", "sma_volume_5",
    "day_of_week", "hour_of_day", "month_of_year",
    "day_monday", "day_tuesday", "day_wednesday", "day_thursday", "day_friday",
    "quarter_1", "quarter_2", "quarter_3", "quarter_4",
    "hour_early_morning", "hour_mid_morning", "hour_afternoon", "hour_late_afternoon",
    "previous_close", "overnight_gap_pct", "overnight_log_return",
    "is_gap_up", "is_gap_down",
]

# ── Feature engineering ────────────────────────────────────────────────────────

def engineer_features(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    df = df.copy()
    df["symbol"]     = symbol
    df["window_ts"]  = pd.to_datetime(df["date"], utc=True)
    df = df.sort_values("window_ts").reset_index(drop=True)
    df["trade_date"] = df["window_ts"].dt.date

    c = df["close"]
    v = df["volume"]

    df["lag_close_1"]  = c.shift(1)
    df["lag_close_5"]  = c.shift(5)
    df["lag_close_10"] = c.shift(10)
    df["close_diff_1"] = c - df["lag_close_1"]
    df["close_diff_5"] = c - df["lag_close_5"]

    df["pct_change_1"] = c.pct_change(1)
    df["pct_change_5"] = c.pct_change(5)
    df["log_return_1"] = np.log(c / df["lag_close_1"])

    df["sma_close_5"]  = c.rolling(5,  min_periods=1).mean()
    df["sma_close_10"] = c.rolling(10, min_periods=1).mean()
    df["sma_close_20"] = c.rolling(20, min_periods=1).mean()
    df["sma_volume_5"] = v.rolling(5,  min_periods=1).mean()

    ts = df["window_ts"]
    df["day_of_week"]   = ts.dt.dayofweek.astype("Int16")
    df["hour_of_day"]   = ts.dt.hour.astype("Int16")
    df["month_of_year"] = ts.dt.month.astype("Int16")

    dow = ts.dt.dayofweek
    df["day_monday"]    = (dow == 0).astype("Int16")
    df["day_tuesday"]   = (dow == 1).astype("Int16")
    df["day_wednesday"] = (dow == 2).astype("Int16")
    df["day_thursday"]  = (dow == 3).astype("Int16")
    df["day_friday"]    = (dow == 4).astype("Int16")

    mo = ts.dt.month
    df["quarter_1"] = mo.isin([1, 2, 3]).astype("Int16")
    df["quarter_2"] = mo.isin([4, 5, 6]).astype("Int16")
    df["quarter_3"] = mo.isin([7, 8, 9]).astype("Int16")
    df["quarter_4"] = mo.isin([10, 11, 12]).astype("Int16")

    hr = ts.dt.hour
    df["hour_early_morning"]  = hr.between(4,  8).astype("Int16")
    df["hour_mid_morning"]    = hr.between(9, 11).astype("Int16")
    df["hour_afternoon"]      = hr.between(12, 14).astype("Int16")
    df["hour_late_afternoon"] = hr.between(15, 20).astype("Int16")

    df["_date"] = ts.dt.date
    daily_last = (
        df.groupby("_date")["close"].last()
        .rename("_prev_close")
        .shift(1)
    )
    df = df.join(daily_last, on="_date")
    df["previous_close"]       = df["_prev_close"]
    df["overnight_gap_pct"]    = (df["open"] - df["_prev_close"]) / df["_prev_close"]
    df["overnight_log_return"] = np.log(df["open"] / df["_prev_close"])
    df["is_gap_up"]            = (df["open"] > df["_prev_close"]).astype("Int16")
    df["is_gap_down"]          = (df["open"] < df["_prev_close"]).astype("Int16")
    df.drop(columns=["_date", "_prev_close"], inplace=True)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Nullify any OHLCV values that would overflow NUMERIC(18,6) — clearly corrupt
    MAX_PRICE = 1e11
    for col in ["open", "high", "low", "close"]:
        df.loc[df[col].abs() > MAX_PRICE, col] = np.nan
    df.loc[df["volume"] > 1e12, "volume"] = np.nan

    # Drop any duplicate timestamps that may exist in the source CSV
    df.drop_duplicates(subset=["symbol", "window_ts"], keep="last", inplace=True)
    return df


# ── Worker (runs in subprocess) ────────────────────────────────────────────────

def _load_symbol(args: tuple) -> tuple[str, int]:
    """Engineer features for one symbol and COPY into Postgres."""
    path, conninfo = args
    symbol = path.stem.upper()

    raw = pd.read_csv(path)
    df  = engineer_features(raw, symbol)
    # Ensure volume stays bigint-compatible after feature engineering
    df["volume"] = df["volume"].fillna(0).astype("int64")

    # Convert to list-of-tuples for COPY — NaN → None
    records = df[COPY_COLS].where(df[COPY_COLS].notna(), other=None).values.tolist()

    copy_sql = (
        f"COPY {TARGET_SCHEMA}.{TARGET_TABLE} "
        f"({', '.join(COPY_COLS)}) FROM STDIN"
    )

    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            with cur.copy(copy_sql) as copy:
                for row in records:
                    copy.write_row(row)
        conn.commit()

    return symbol, len(records)


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Load final_data CSVs → ml.market_data_15m (parallelised)")
    p.add_argument("--symbols",  default="ALL",
                   help="Comma-separated symbols or ALL (default: ALL)")
    p.add_argument("--truncate", action="store_true",
                   help="Truncate ml.market_data_15m before loading")
    p.add_argument("--workers",  type=int, default=None,
                   help="Worker processes (default: min(cpu_count, 28))")
    p.add_argument("--host",     default=None)
    p.add_argument("--port",     type=int, default=None)
    p.add_argument("--db",       default=None)
    p.add_argument("--user",     default=None)
    p.add_argument("--password", default=None)
    return p.parse_args()


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    load_dotenv(ML_ROOT.parent / "backend" / ".env")
    load_dotenv(ML_ROOT / ".env", override=False)

    args = parse_args()

    host     = args.host     or os.getenv("POSTGRES_SERVER", DEFAULT_HOST)
    port     = args.port     or int(os.getenv("POSTGRES_PORT", DEFAULT_PORT))
    db       = args.db       or os.getenv("POSTGRES_DB",     DEFAULT_DB)
    user     = args.user     or os.getenv("POSTGRES_USER",   DEFAULT_USER)
    password = args.password or os.getenv("POSTGRES_PASSWORD", DEFAULT_PASS)
    conninfo = f"host={host} port={port} dbname={db} user={user} password={password}"

    n_workers = args.workers or min(multiprocessing.cpu_count(), 28)

    # Resolve CSV files
    if args.symbols.upper() == "ALL":
        files = sorted(FINAL_DATA_DIR.glob("*.csv"))
    else:
        symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
        files   = [FINAL_DATA_DIR / f"{s}.csv" for s in symbols]

    missing = [str(f) for f in files if not f.exists()]
    if missing:
        raise FileNotFoundError(f"Missing: {', '.join(missing)}")

    print(f"[connect]  {user}@{host}:{port}/{db}")
    print(f"[symbols]  {len(files)}  [workers]  {n_workers}")

    # Setup schema/table and optionally truncate (single connection, before workers start)
    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            if args.truncate:
                print(f"[truncate] {TARGET_SCHEMA}.{TARGET_TABLE}")
                cur.execute(
                    f"TRUNCATE TABLE {TARGET_SCHEMA}.{TARGET_TABLE} RESTART IDENTITY"
                )
        conn.commit()

    # Parallel load
    t0    = time.perf_counter()
    total = 0
    done  = 0
    work  = [(f, conninfo) for f in files]

    with ProcessPoolExecutor(max_workers=n_workers) as pool:
        futures = {pool.submit(_load_symbol, w): w[0].stem for w in work}
        for fut in as_completed(futures):
            symbol, n = fut.result()
            total += n
            done  += 1
            elapsed = time.perf_counter() - t0
            rate = total / elapsed if elapsed > 0 else 0
            print(
                f"[{done:>3}/{len(files)}] {symbol:<6}  {n:>7,} rows  "
                f"| total {total:>10,}  {rate:,.0f} rows/s",
                flush=True,
            )

    elapsed = time.perf_counter() - t0
    print(f"\n[done] {len(files)} symbols  {total:,} rows  {elapsed:.1f}s  "
          f"({total/elapsed:,.0f} rows/s) → {TARGET_SCHEMA}.{TARGET_TABLE}")


if __name__ == "__main__":
    main()
