# Current Database Inventory

Snapshot date: 2026-04-08

Database inspected: `app`

This document only describes the current active data layer and current local data assets. Legacy schemas and old table layouts are intentionally omitted here.

## Current System

- Active feature store: `ml.market_data_15m`
- Active macro table: `ml.macro_indicator_daily`
- Current symbol coverage: 505 symbols
- Current trading-date coverage: 525 dates
- Current date range: `2024-03-25` to `2026-04-07`
- Current inference path: reads engineered rows from `ml.market_data_15m`
- Current training default source: `ml.market_data_15m`
- Current parquet usage: optional local input/export, not the default runtime source

## Database Size

Live size snapshot from Postgres:

| Object | Size |
| --- | --- |
| Database `app` | 9140 MB |
| `ml.market_data_15m` total | 8421 MB |
| `ml.market_data_15m` table heap | 6743 MB |
| `ml.market_data_15m` indexes | 1676 MB |
| `ml.macro_indicator_daily` total | 264 kB |

The main storage footprint is `ml.market_data_15m`.

## Active Tables

### `ml.market_data_15m`

This is the active market-data and feature table used by the current ML system.

| Metric | Value |
| --- | --- |
| Rows | 6,636,640 |
| Symbols | 505 |
| Trading dates | 525 |
| Date range | 2024-03-25 to 2026-04-07 |
| Avg bars per symbol-day | 25.84 |
| Status values | `confirmed` only |

Columns present:

```text
agg_id, symbol, trade_date, window_ts, open, high, low, close, volume,
slot_count, status, created_at, lag_close_1, lag_close_5, lag_close_10,
close_diff_1, close_diff_5, pct_change_1, pct_change_5, log_return_1,
sma_close_5, sma_close_10, sma_close_20, sma_volume_5, day_of_week,
hour_of_day, day_monday, day_tuesday, day_wednesday, day_thursday,
day_friday, quarter_1, quarter_2, quarter_3, quarter_4,
hour_early_morning, hour_mid_morning, hour_afternoon, hour_late_afternoon,
previous_close, overnight_gap_pct, overnight_log_return, is_gap_up,
is_gap_down, month_of_year
```

Feature groups in this table:

- OHLCV bars
- lag and delta features
- rolling averages
- weekday, month, quarter, and hour features
- session-bucket flags
- overnight gap context

### `ml.macro_indicator_daily`

This is the active macro side table used alongside the market feature store.

| Metric | Value |
| --- | --- |
| Rows | 1,524 |
| Distinct series | 3 |
| Date range | 2024-03-25 to 2026-04-07 |

Series currently present:

| Series code | Rows |
| --- | ---: |
| `US_TREASURY_10Y` | 508 |
| `US_TREASURY_13W` | 508 |
| `US_TREASURY_5Y` | 508 |

Columns present:

```text
series_code, trade_date, value, source, created_at
```

## Current Parquet Assets

The active training script defaults to the database table `ml.market_data_15m`. Parquet is optional through `--source-parquet`.

Current local parquet files of interest:

| File | Size | Notes |
| --- | --- | --- |
| `ml/data/market_data_15m.parquet` | 428,009,984 bytes | Main local parquet export of the active feature-store shape |
| `ml/data/datasets/snapshot_ALL_20260303_074426.parquet` | 81,278,831 bytes | Snapshot dataset |
| `ml/data/datasets/snapshot_ALL_20260303_074412.parquet` | 81,278,831 bytes | Snapshot dataset |

There are also many smaller raw vendor parquet files under `ml/data/raw_market_vendor/intraday/`.

## Current Scripts

These are the scripts that matter for the active dataset:

- [ml/scripts/refetch_market_data_15m_quality.py](../ml/scripts/refetch_market_data_15m_quality.py)
  Main bulk backfill and quality workflow writing into `ml.market_data_15m` and `ml.macro_indicator_daily`.
- [ml/scripts/backfill_market_data_15m_from_fmp.py](../ml/scripts/backfill_market_data_15m_from_fmp.py)
  Targeted FMP backfill/upsert workflow for `ml.market_data_15m`.
- [ml/scripts/fetch_raw_market_vendor_dataset.py](../ml/scripts/fetch_raw_market_vendor_dataset.py)
  Raw vendor-data acquisition helper.
- [ml/XG_boost_3_multigpu_final.py](../ml/XG_boost_3_multigpu_final.py)
  Current training entrypoint. Default source is `ml.market_data_15m`; parquet is optional via `--source-parquet`.

## What The Model Makes

The current model does not just make one next-price number.

It makes:

1. A 26-bar next-trading-session 15-minute predicted close path.
2. A full-day predicted return from the last predicted bar versus current price.
3. A direction label: `up` or `down`.
4. A model version identifier.

Each predicted path row contains:

- `bar_idx`
- `bar_time`
- `pred_close`

The active inference path reads recent engineered rows from `ml.market_data_15m`, rebuilds the production feature vector, predicts 26 log-returns, and converts them into 26 absolute predicted close prices.

## Short Answer

If the question is "what do we currently have and use", the answer is:

- database table `ml.market_data_15m`
- macro table `ml.macro_indicator_daily`
- optional local parquet export `ml/data/market_data_15m.parquet`
- current backfill and training scripts around that same data model

## Reference Pointers

- Root project docs: [README.md](../README.md)
- ML docs index: [ml/README.md](../ml/README.md)
- April 7 replay note: [ml/SIMULATION_APRIL7.md](../ml/SIMULATION_APRIL7.md)
