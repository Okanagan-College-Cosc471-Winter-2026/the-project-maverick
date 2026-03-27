#!/usr/bin/env python3
"""
debug_pipeline.py — Step-by-step diagnosis of why train_ready has only 6 dates.
Run on DRAC: python3 debug_pipeline.py
"""
import sys
sys.path.insert(0, "/project/6065705")

import numpy as np
import pandas as pd

PARQUET = "/project/6065705/market_data_15m.parquet"
EXPECTED_REGULAR_BARS = 26
REGULAR_OPEN_MINUTE  = 9 * 60 + 30   # 570
REGULAR_CLOSE_MINUTE = 16 * 60        # 960

print("=" * 60)
print("Step 1: Load parquet")
df = pd.read_parquet(PARQUET, engine="pyarrow")
print(f"  rows        : {len(df):,}")
print(f"  trade_date  : dtype={df['trade_date'].dtype}  unique={df['trade_date'].nunique()}")
print(f"  window_ts   : dtype={df['window_ts'].dtype}")
print(f"  status      : {df['status'].unique()}")
print(f"  min date    : {df['trade_date'].min()}")
print(f"  max date    : {df['trade_date'].max()}")

print()
print("Step 2: Simulate load_bars (18-month window)")
df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce").dt.normalize()
requested_as_of = pd.Timestamp(df["window_ts"].max()).normalize()
load_start = (requested_as_of - pd.DateOffset(months=18)).strftime("%Y-%m-%d")
load_end   = requested_as_of.strftime("%Y-%m-%d")
print(f"  requested_as_of : {requested_as_of.date()}")
print(f"  load_start      : {load_start}")
print(f"  load_end        : {load_end}")

start_ts = pd.Timestamp(load_start).normalize()
end_ts   = pd.Timestamp(load_end).normalize()
bars = df[df["trade_date"].between(start_ts, end_ts)].copy()
print(f"  bars after date filter: {len(bars):,}  dates={bars['trade_date'].nunique()}")

print()
print("Step 3: Check bars per session (complete_sessions)")
session_counts = (
    bars.groupby(["symbol", "trade_date"])
    .size()
    .rename("bar_count")
    .reset_index()
)
dist = session_counts["bar_count"].value_counts().sort_index()
print(f"  bar_count distribution (top 10):")
for cnt, n in dist.items():
    print(f"    {int(cnt):3d} bars: {n:,} sessions")

complete = session_counts[session_counts["bar_count"] == EXPECTED_REGULAR_BARS]
print(f"  complete sessions (bar_count==26): {len(complete):,}")
print(f"  unique dates in complete sessions: {complete['trade_date'].nunique()}")

print()
print("Step 4: Check slot_idx via cumcount")
bars_sorted = bars.sort_values(["symbol", "trade_date", "window_ts"])
bars_sorted["slot_idx"] = bars_sorted.groupby(["symbol", "trade_date"]).cumcount()
slot_dist = bars_sorted["slot_idx"].value_counts().sort_index()
print(f"  slot_idx range: {bars_sorted['slot_idx'].min()} – {bars_sorted['slot_idx'].max()}")
print(f"  rows with slot_idx == 25: {(bars_sorted['slot_idx'] == 25).sum():,}")

print()
print("Step 5: Simulate build_next_session_targets")
bars_complete = bars_sorted.merge(complete[["symbol", "trade_date"]], on=["symbol", "trade_date"])
session_meta = (
    bars_complete[["symbol", "trade_date"]]
    .drop_duplicates()
    .sort_values(["symbol", "trade_date"])
    .reset_index(drop=True)
)
session_meta["next_trade_date"] = session_meta.groupby("symbol")["trade_date"].shift(-1)

try:
    next_close_wide = bars_complete.pivot(
        index=["symbol", "trade_date"], columns="slot_idx", values="close"
    )
    next_close_wide = next_close_wide.reindex(columns=list(range(EXPECTED_REGULAR_BARS)))
    next_close_wide.columns = [f"next_close_h{int(s):02d}" for s in next_close_wide.columns]
    next_close_wide = next_close_wide.reset_index().rename(columns={"trade_date": "next_trade_date"})
    target_frame = session_meta.merge(next_close_wide, on=["symbol", "next_trade_date"], how="left")
    TARGET_COLS = [f"next_close_h{s:02d}" for s in range(26)]
    nan_targets = target_frame[TARGET_COLS].isna().all(axis=1).sum()
    valid_targets = target_frame[TARGET_COLS].notna().all(axis=1).sum()
    print(f"  target_frame rows       : {len(target_frame):,}")
    print(f"  rows with ALL targets   : {valid_targets:,}")
    print(f"  rows with NO targets    : {nan_targets:,}")
    print(f"  unique dates w/ targets : {target_frame[target_frame[TARGET_COLS[0]].notna()]['trade_date'].nunique()}")
except Exception as e:
    print(f"  PIVOT ERROR: {e}")

print()
print("=" * 60)
print("Done.")
