#!/usr/bin/env python3
"""
export_parquet.py — Export ml.market_data_15m → Parquet for DRAC/Nibi training.

Reads the full ml.market_data_15m table from Docker Postgres and writes a
single compressed Parquet file ready to copy to the cluster.

Usage:
    python ml/scripts/data_prep/export_parquet.py
    python ml/scripts/data_prep/export_parquet.py --out ml/data/market_data_15m.parquet
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv
import os

ML_ROOT  = Path(__file__).resolve().parents[3] / "ml"
DEFAULT_OUT = ML_ROOT / "data" / "market_data_15m.parquet"

CONNINFO = "host=localhost port=5432 dbname=app user=postgres password=changethis"

QUERY = """
SELECT
    symbol, trade_date, window_ts,
    open, high, low, close, volume,
    lag_close_1, lag_close_5, lag_close_10,
    close_diff_1, close_diff_5,
    pct_change_1, pct_change_5, log_return_1,
    sma_close_5, sma_close_10, sma_close_20, sma_volume_5,
    day_of_week, hour_of_day, month_of_year,
    day_monday, day_tuesday, day_wednesday, day_thursday, day_friday,
    quarter_1, quarter_2, quarter_3, quarter_4,
    hour_early_morning, hour_mid_morning, hour_afternoon, hour_late_afternoon,
    previous_close, overnight_gap_pct, overnight_log_return,
    is_gap_up, is_gap_down,
    slot_count, status
FROM ml.market_data_15m
WHERE symbol = %s
ORDER BY window_ts
"""

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    return p.parse_args()

def main():
    load_dotenv(ML_ROOT.parent / "backend" / ".env")

    args  = parse_args()
    out   = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    SMALLINT_COLS = [
        "day_of_week", "hour_of_day", "month_of_year",
        "day_monday", "day_tuesday", "day_wednesday", "day_thursday", "day_friday",
        "quarter_1", "quarter_2", "quarter_3", "quarter_4",
        "hour_early_morning", "hour_mid_morning", "hour_afternoon", "hour_late_afternoon",
        "is_gap_up", "is_gap_down",
    ]

    print(f"[query] streaming ml.market_data_15m by symbol ...")
    t0 = time.perf_counter()

    import pyarrow as pa
    import pyarrow.parquet as pq

    # Fixed schema — float32 for all price/feature cols to keep file small
    FLOAT_COLS = [
        "open", "high", "low", "close",
        "lag_close_1", "lag_close_5", "lag_close_10",
        "close_diff_1", "close_diff_5",
        "pct_change_1", "pct_change_5", "log_return_1",
        "sma_close_5", "sma_close_10", "sma_close_20", "sma_volume_5",
        "previous_close", "overnight_gap_pct", "overnight_log_return",
    ]

    SCHEMA = pa.schema([
        ("symbol",             pa.string()),
        ("trade_date",         pa.date32()),
        ("window_ts",          pa.timestamp("us", tz="UTC")),
        *[(c,                  pa.float32()) for c in FLOAT_COLS],
        ("volume",             pa.int64()),
        ("day_of_week",        pa.int8()),
        ("hour_of_day",        pa.int8()),
        ("month_of_year",      pa.int8()),
        ("day_monday",         pa.int8()),
        ("day_tuesday",        pa.int8()),
        ("day_wednesday",      pa.int8()),
        ("day_thursday",       pa.int8()),
        ("day_friday",         pa.int8()),
        ("quarter_1",          pa.int8()),
        ("quarter_2",          pa.int8()),
        ("quarter_3",          pa.int8()),
        ("quarter_4",          pa.int8()),
        ("hour_early_morning", pa.int8()),
        ("hour_mid_morning",   pa.int8()),
        ("hour_afternoon",     pa.int8()),
        ("hour_late_afternoon",pa.int8()),
        ("is_gap_up",          pa.int8()),
        ("is_gap_down",        pa.int8()),
        ("slot_count",         pa.int32()),
        ("status",             pa.string()),
    ])

    writer = None
    total  = 0

    with psycopg.connect(CONNINFO) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT symbol FROM ml.market_data_15m ORDER BY symbol")
            symbols = [r[0] for r in cur.fetchall()]

        for i, symbol in enumerate(symbols, 1):
            with conn.cursor() as cur:
                cur.execute(QUERY, (symbol,))
                cols = [d.name for d in cur.description]
                rows = cur.fetchall()

            chunk = pd.DataFrame(rows, columns=cols)
            for col in FLOAT_COLS:
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce").astype("float32")
            for col in SMALLINT_COLS:
                chunk[col] = chunk[col].astype("Int8")
            chunk["volume"]     = chunk["volume"].fillna(0).astype("int64")
            chunk["slot_count"] = chunk["slot_count"].fillna(0).astype("int32")
            chunk["status"]     = chunk["status"].fillna("provisional").astype(str)

            table = pa.Table.from_pandas(chunk[list(SCHEMA.names)], schema=SCHEMA, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(out, SCHEMA, compression="snappy")
            writer.write_table(table)
            total += len(chunk)
            print(f"[{i:>3}/{len(symbols)}] {symbol:<6}  {len(chunk):>7,} rows  total {total:>10,}", flush=True)

    if writer:
        writer.close()

    elapsed = time.perf_counter() - t0

    size_mb = out.stat().st_size / 1024 / 1024
    print(f"[done]  {out.name}  {size_mb:.1f} MB  written in {elapsed:.1f}s")
    print(f"\nTo copy to DRAC Nibi:")
    print(f"  rsync -avz --progress {out} <user>@nibi.alliancecan.ca:~/scratch/")

if __name__ == "__main__":
    main()
