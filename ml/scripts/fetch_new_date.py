"""
fetch_new_date.py — Fetch a completely new trading date from FMP and insert
into ml.market_data_15m with all engineered features computed.

Usage:
    python ml/scripts/fetch_new_date.py --date 2026-04-08
    python ml/scripts/fetch_new_date.py --date 2026-04-08 --limit 10   # test first 10 symbols
"""

from __future__ import annotations

import argparse
import sys
import os
from datetime import date

# Reuse all logic from the existing backfill script
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util, types

# Load the backfill module without executing main()
spec = importlib.util.spec_from_file_location(
    "backfill",
    os.path.join(os.path.dirname(__file__), "backfill_market_data_15m_from_fmp.py"),
)
mod = importlib.util.module_from_spec(spec)
sys.modules["backfill"] = mod   # register before exec so @dataclass resolves __module__
spec.loader.exec_module(mod)

Candidate          = mod.Candidate
fetch_fmp_symbol_range   = mod.fetch_fmp_symbol_range
prepare_upsert_rows      = mod.prepare_upsert_rows
upsert_core_rows         = mod.upsert_core_rows
load_symbol_window       = mod.load_symbol_window
recompute_features       = mod.recompute_features
update_features          = mod.update_features
connect_db               = mod.connect_db


def main():
    parser = argparse.ArgumentParser(description="Fetch a completely new trading date into ml.market_data_15m.")
    parser.add_argument("--date", required=True, help="Trading date to fetch (YYYY-MM-DD).")
    parser.add_argument("--limit", type=int, default=None, help="Limit to first N symbols (for testing).")
    parser.add_argument("--dry-run", action="store_true", help="Fetch but don't write to DB.")
    args = parser.parse_args()

    target = date.fromisoformat(args.date)

    conn = connect_db()
    cur = conn.cursor()

    # Get all symbols that have data the day before (proxy for "active symbols")
    cur.execute(
        "SELECT DISTINCT symbol FROM ml.market_data_15m WHERE trade_date = %s ORDER BY symbol",
        (target - __import__("datetime").timedelta(days=1),),
    )
    rows = cur.fetchall()
    if not rows:
        # Fall back to latest available date
        cur.execute("SELECT DISTINCT symbol FROM ml.market_data_15m ORDER BY symbol")
        rows = cur.fetchall()

    symbols = [r[0] for r in rows]
    if args.limit:
        symbols = symbols[: args.limit]

    print(f"Fetching {len(symbols)} symbols for {target} from FMP...")

    # Build synthetic candidate list: one per expected bar per symbol
    # We don't know exact bar times yet — use the fetch+prepare pipeline
    # which discovers bars from the FMP response.
    fetched_by_symbol: dict = {}
    candidates: list = []

    for i, symbol in enumerate(symbols, 1):
        df = fetch_fmp_symbol_range(symbol, target, target)
        if df.empty:
            print(f"  [{i}/{len(symbols)}] {symbol}: no data from FMP")
            continue
        # Filter to target date only (FMP may return adjacent days)
        df = df[df["trade_date"] == target]
        if df.empty:
            print(f"  [{i}/{len(symbols)}] {symbol}: no bars for {target} after filtering")
            continue
        fetched_by_symbol[symbol] = df
        for _, row in df.iterrows():
            candidates.append(Candidate(
                symbol=symbol,
                trade_date=target,
                expected_ts_utc=row["window_ts"],
                reason="new_date",
            ))
        print(f"  [{i}/{len(symbols)}] {symbol}: {len(df)} bars")

    if not candidates:
        print("No data fetched from FMP — check API key and date.")
        return

    print(f"\nPreparing {len(candidates)} rows for upsert...")
    upsert_rows, affected, skipped = prepare_upsert_rows(candidates, fetched_by_symbol)

    if args.dry_run:
        print(f"DRY RUN: would upsert {len(upsert_rows)} rows. Skipped {len(skipped)}.")
        conn.close()
        return

    print(f"Upserting {len(upsert_rows)} core rows...")
    upsert_core_rows(conn, upsert_rows)
    conn.commit()

    # Recompute features for each symbol
    print("Recomputing engineered features...")
    total_updated = 0
    for symbol, dates in affected.items():
        frame = load_symbol_window(conn, symbol, dates)
        if frame.empty:
            continue
        recomputed = recompute_features(frame)
        n = update_features(conn, symbol, recomputed, dates)
        total_updated += n
        conn.commit()

    print(f"\nDone. {total_updated} feature rows updated for {target}.")
    conn.close()


if __name__ == "__main__":
    main()
