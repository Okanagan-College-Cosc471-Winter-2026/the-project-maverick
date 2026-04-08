# Current Database Inventory

Snapshot date: 2026-04-08
Database inspected: `app`

This document summarizes what is currently present in the local Postgres database, which schemas are actually populated, and which tables appear to be legacy or scaffolded but empty.

## Executive Summary

- The active data layer is the `ml` schema, especially `ml.market_data_15m`.
- The strongest live dataset is the 15-minute feature store used by training and replay.
- `market_intraday.prices_5min` is also populated and appears to be a legacy raw intraday source.
- The `dw` warehouse structure exists, including 96 monthly partitions, but is currently empty.
- The `market` schema contains 29 symbol tables plus `market.stocks`, but the registry table is empty.
- `public.alembic_version` exists but currently has no version row.

## Schema Overview

| Schema | Base tables | Current status |
| --- | ---: | --- |
| `ml` | 2 | Active and populated |
| `market_intraday` | 1 | Active and populated |
| `market` | 30 | Partially populated legacy layer |
| `dw` | 103 | Present but empty |
| `public` | 1 | Migration bookkeeping table present, no version row |

## What We Have Now

### `ml` schema

#### `ml.market_data_15m`

Primary feature store for the current ML pipeline.

| Metric | Value |
| --- | --- |
| Rows | 6,636,640 |
| Symbols | 505 |
| Trade dates | 525 |
| Date range | 2024-03-25 to 2026-04-07 |
| Avg bars per symbol-day | 25.84 |
| Status values | `confirmed` only |

Schema:

| Column group | Columns |
| --- | --- |
| Identity and time | `agg_id`, `symbol`, `trade_date`, `window_ts`, `created_at` |
| OHLCV | `open`, `high`, `low`, `close`, `volume` |
| Session tracking | `slot_count`, `status` |
| Lag and delta features | `lag_close_1`, `lag_close_5`, `lag_close_10`, `close_diff_1`, `close_diff_5`, `pct_change_1`, `pct_change_5`, `log_return_1` |
| Rolling features | `sma_close_5`, `sma_close_10`, `sma_close_20`, `sma_volume_5` |
| Calendar features | `day_of_week`, `hour_of_day`, `month_of_year` |
| One-hot weekday features | `day_monday`, `day_tuesday`, `day_wednesday`, `day_thursday`, `day_friday` |
| One-hot quarter features | `quarter_1`, `quarter_2`, `quarter_3`, `quarter_4` |
| One-hot intraday bucket features | `hour_early_morning`, `hour_mid_morning`, `hour_afternoon`, `hour_late_afternoon` |
| Overnight context | `previous_close`, `overnight_gap_pct`, `overnight_log_return`, `is_gap_up`, `is_gap_down` |

#### `ml.macro_indicator_daily`

Daily macro feature table aligned to trading dates.

| Metric | Value |
| --- | --- |
| Rows | 1,524 |
| Distinct series | 3 |
| Date range | 2024-03-25 to 2026-04-07 |

Schema:

| Column | Type |
| --- | --- |
| `series_code` | text |
| `trade_date` | date |
| `value` | numeric |
| `source` | text |
| `created_at` | timestamptz |

### `market_intraday` schema

#### `market_intraday.prices_5min`

Legacy or raw intraday bar store at 5-minute granularity.

| Metric | Value |
| --- | --- |
| Rows | 4,027,712 |
| Date range | 2020-08-03 to 2026-03-03 |

Schema:

| Column | Type |
| --- | --- |
| `id` | bigint |
| `symbol` | text |
| `ts` | timestamp |
| `open` | double precision |
| `high` | double precision |
| `low` | double precision |
| `close` | double precision |
| `volume` | bigint |
| `source_file` | text |
| `created_at` | timestamptz |

### `market` schema

The schema contains the following base tables:

- 29 symbol-specific tables: `AAPL`, `AMD`, `AMZN`, `BA`, `BABA`, `BAC`, `C`, `CSCO`, `CVX`, `DIS`, `F`, `GE`, `GOOGL`, `IBM`, `INTC`, `JNJ`, `JPM`, `KO`, `MCD`, `META`, `MSFT`, `NFLX`, `NVDA`, `PFE`, `T`, `TSLA`, `VZ`, `WMT`, `XOM`
- 1 registry table: `market.stocks`

`market.stocks` summary:

| Metric | Value |
| --- | --- |
| Rows | 0 |
| Active symbols flagged | 0 |

Schema:

| Column | Type |
| --- | --- |
| `symbol` | text |
| `name` | text |
| `sector` | text |
| `industry` | text |
| `exchange` | text |
| `is_active` | boolean |
| `currency` | text |

### `dw` schema

Warehouse structure exists but is currently empty.

Summary:

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

Key fact schema:

| Column | Type |
| --- | --- |
| `sk_fact_id` | bigint |
| `fk_date_id` | bigint |
| `fk_instrument_id` | bigint |
| `fk_exchange_id` | bigint |
| `fk_audit_id` | bigint |
| `fk_company_id` | bigint |
| `trade_count` | integer |
| `open_price` | numeric |
| `high_price` | numeric |
| `low_price` | numeric |
| `close_price` | numeric |
| `volume` | bigint |
| `adj_close` | numeric |
| `vwap` | numeric |
| `previous_close` | numeric |
| `price_change` | numeric |
| `price_change_pct` | numeric |
| `price_range` | numeric |

### `public` schema

| Table | Status |
| --- | --- |
| `alembic_version` | Present but empty |

## Interpretation

- If the question is "what database do we actively use for training and replay right now," the answer is `ml.market_data_15m` plus `ml.macro_indicator_daily`.
- If the question is "what legacy/raw intraday data still exists," the answer is `market_intraday.prices_5min` and the symbol-specific tables in `market`.
- If the question is "is the warehouse layer live right now," the answer is no: the `dw` schema is structurally present but not populated in this database snapshot.

## Recommended Reference Pointers

- Root project docs: [README.md](/home/cosc-admin/the-project-maverick/README.md)
- ML docs index: [ml/README.md](/home/cosc-admin/the-project-maverick/ml/README.md)
- April 7 replay note: [ml/SIMULATION_APRIL7.md](/home/cosc-admin/the-project-maverick/ml/SIMULATION_APRIL7.md)
