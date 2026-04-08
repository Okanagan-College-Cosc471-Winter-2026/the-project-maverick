# Current Database Inventory

Snapshot date: 2026-04-08

Database inspected: `app`

Inspection source: live queries against the running Postgres container:

```bash
docker compose exec -T db psql -U postgres -d app
```

This document describes what is actually present in the local database on April 8, 2026. It is based on live SQL queries, not historical assumptions.

## Executive Summary

- The active ML data layer is the `ml` schema.
- The main feature store is `ml.market_data_15m` with 6,636,640 rows across 505 symbols.
- The macro side table `ml.macro_indicator_daily` is populated and contains 3 Treasury series.
- `market_intraday.prices_5min` still exists as a populated legacy/raw intraday table.
- The `market` schema exists, but all 29 symbol tables and `market.stocks` currently show zero live rows.
- The `dw` warehouse structure exists, including 96 monthly partitions, but the key warehouse tables checked in this snapshot are empty.
- `public.alembic_version` exists but currently has no version row.

## Schema Summary

| Schema | Base tables | Live status | Notes |
| --- | ---: | --- | --- |
| `ml` | 2 | Active and populated | Current feature store for training, inference, and replay support |
| `market_intraday` | 1 | Populated | Legacy/raw 5-minute bar store |
| `market` | 30 | Present but effectively empty | 29 symbol tables plus `market.stocks`, all currently at zero live rows |
| `dw` | 103 | Structure only | Warehouse tables and partitions exist, but sampled core tables are empty |
| `public` | 1 | Bookkeeping only | `alembic_version` table exists with zero rows |

## Active ML Layer

### `ml.market_data_15m`

This is the current core feature store.

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

Feature families represented in this table:

- Base market bars: open, high, low, close, volume
- Session structure: `slot_count`, `status`, `window_ts`
- Lag and delta features: lagged closes, close deltas, percent changes, log return
- Rolling features: short moving averages for price and volume
- Calendar features: weekday, hour, month, quarter
- One-hot time buckets: weekday flags, quarter flags, intraday bucket flags
- Overnight context: previous close, overnight gap metrics, gap direction flags

This is the table the current inference feature reconstruction reads from for live next-day path prediction.

### `ml.macro_indicator_daily`

Daily macro inputs aligned to trading dates.

| Metric | Value |
| --- | --- |
| Rows | 1,524 |
| Distinct series | 3 |
| Date range | 2024-03-25 to 2026-04-07 |

Series currently present:

| Series code | Rows | Date range |
| --- | ---: | --- |
| `US_TREASURY_10Y` | 508 | 2024-03-25 to 2026-04-07 |
| `US_TREASURY_13W` | 508 | 2024-03-25 to 2026-04-07 |
| `US_TREASURY_5Y` | 508 | 2024-03-25 to 2026-04-07 |

Columns present:

```text
series_code, trade_date, value, source, created_at
```

## Legacy and Empty Layers

### `market_intraday.prices_5min`

This table is populated and appears to be the main legacy/raw intraday store.

| Metric | Value |
| --- | --- |
| Rows | 4,027,712 |
| Timestamp range | 2020-08-03 04:00:00 to 2026-03-03 13:25:00 |

Columns present:

```text
id, symbol, ts, open, high, low, close, volume, source_file, created_at
```

### `market` schema

The `market` schema contains 30 base tables:

- 29 symbol tables: `AAPL`, `AMD`, `AMZN`, `BA`, `BABA`, `BAC`, `C`, `CSCO`, `CVX`, `DIS`, `F`, `GE`, `GOOGL`, `IBM`, `INTC`, `JNJ`, `JPM`, `KO`, `MCD`, `META`, `MSFT`, `NFLX`, `NVDA`, `PFE`, `T`, `TSLA`, `VZ`, `WMT`, `XOM`
- 1 registry table: `market.stocks`

Observed status:

- `market.stocks` exact row count: 0
- `market.stocks` active symbols flagged: 0
- Estimated live rows from `pg_stat_user_tables`: 0 across all 29 symbol tables and `market.stocks`

`market.stocks` columns:

```text
symbol, name, sector, industry, exchange, is_active, currency
```

### `dw` schema

The warehouse layout is present, but the core tables checked in this snapshot are empty.

| Metric | Value |
| --- | --- |
| Base tables | 103 |
| Monthly `fact_stock_YYYYMM` partitions | 96 |
| `dw.fact_15min_stock_price` rows | 0 |
| `dw.dim_company` rows | 0 |
| `dw.dim_date` rows | 0 |
| `dw.dim_exchange` rows | 0 |
| `dw.dim_instrument` rows | 0 |
| `dw.dim_meta_audit_log` rows | 0 |

Key fact table columns:

```text
sk_fact_id, fk_date_id, fk_instrument_id, fk_exchange_id, fk_audit_id,
fk_company_id, trade_count, open_price, high_price, low_price, close_price,
volume, adj_close, vwap, previous_close, price_change, price_change_pct,
price_range
```

### `public` schema

| Table | Status |
| --- | --- |
| `public.alembic_version` | Present, exact row count is 0 |

## What The Current ML Model Makes

The live inference contract is no longer a single next-price prediction. The active inference path produces a full next-session intraday path.

Current model output shape:

- `symbol`
- `current_price`
- `prediction_date`
- `predicted_full_day_return`
- `predicted_direction`
- `path` with 26 predicted 15-minute bars
- `model_version`

Each entry in `path` contains:

- `bar_idx`
- `bar_time`
- `pred_close`

In practical terms, the current model makes:

1. A predicted 26-bar next-day 15-minute close path.
2. A full-day return estimate from the last predicted bar versus the current price.
3. A direction label: `up` or `down`.
4. A model version identifier for the artifact bundle used.

Implementation notes from the current backend:

- The inference service reads recent engineered rows from `ml.market_data_15m`.
- It reconstructs the production feature vector from that history.
- The model predicts 26 log-returns.
- The backend converts those log-returns into 26 absolute predicted close prices.

So the best short description is:

> The current ML model predicts the next trading session's full 15-minute price path, not just a single price.

## Interpretation

- If the question is "what data do we actively use for the current ML feature store," the answer is `ml.market_data_15m` plus `ml.macro_indicator_daily`.
- If the question is "what older intraday data still exists," the answer is `market_intraday.prices_5min`.
- If the question is "is the `market` schema live," the answer is effectively no in this snapshot because its tables currently show zero live rows.
- If the question is "is the warehouse live," the answer is no in this snapshot because the checked `dw` fact and dimension tables are empty.

## Reference Pointers

- Root project docs: [README.md](../README.md)
- ML docs index: [ml/README.md](../ml/README.md)
- April 7 replay note: [ml/SIMULATION_APRIL7.md](../ml/SIMULATION_APRIL7.md)
