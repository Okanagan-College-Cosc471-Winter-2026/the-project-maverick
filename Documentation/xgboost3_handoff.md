# XG_boost_3.py Teammate Handoff

This document is the fastest way to understand what [scripts/XG_boost_3.py](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py) is doing and how to work with it.

It is written for a teammate who needs the mental model first and the implementation details second.

Related docs:

- Production mode details: [production_nextday.md](/Volumes/Transcend/COSC471/docs/production_nextday.md)
- Intraday replay details: [replay_nextday_intraday.md](/Volumes/Transcend/COSC471/docs/replay_nextday_intraday.md)

## One Sentence Summary

`XG_boost_3.py` trains and serves a next-day forecast for the **entire next regular trading session 15-minute close path** using today's completed regular session, premarket summary information, and rolling history.

## What Problem It Solves

The script does **not** predict just one scalar return.

It predicts the next trading day's regular-session path as `26` separate 15-minute horizons:

- `target_h00` = first regular 15-minute close of the next session
- `target_h25` = last regular 15-minute close of the next session

Each target is a log return relative to a reference price:

- Production training target: `log(next_day_regular_close_h / current_day_last_regular_close)`
- Replay target: `log(next_day_regular_close_h / current_day_cutoff_regular_close)`

Those definitions are declared near the top of the file at [XG_boost_3.py:68](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L68).

## The Core Mental Model

Think of the script as a pipeline with five stages:

1. Load raw 15-minute bars from the `dw` warehouse.
2. Convert them into one row per `symbol x trade_date`.
3. Expand that row into a wide feature table.
4. Train `26` XGBoost regressors, one per horizon.
5. Save the resulting bundle and use it for prediction or promotion.

The training bundle is therefore a **set of models**, not a single model file.

## Inputs

The source data comes from the `dw` schema:

- `dw.fact_15min_stock_price`
- `dw.dim_date`
- `dw.dim_instrument`
- `dw.dim_exchange`
- `dw.dim_company`

That join is defined in [XG_boost_3.py:266](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L266).

Important assumptions:

- Bars are 15-minute bars.
- A complete regular session has `26` bars.
- The script separates premarket bars from regular-session bars.
- Only complete regular sessions are eligible for the main production dataset.

## Feature Families

The main feature builder is [build_symbol_day_dataset()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L404).

It creates four broad feature groups.

### 1. Daily Summary Features

These summarize the current full regular session:

- `day_open`
- `day_close`
- `day_high`
- `day_low`
- `day_volume`
- `day_trades`
- `day_vwap`
- `full_day_return`
- `day_range`
- `overnight_gap`
- `day_vwap_delta`
- `day_realized_vol`

### 2. Premarket Features

These summarize the current premarket session when present:

- `premarket_open`
- `premarket_close`
- `premarket_high`
- `premarket_low`
- `premarket_volume`
- `premarket_trades`
- `premarket_return`
- `premarket_range`
- `premarket_gap`
- `premarket_close_to_prev_close`
- `premarket_vwap_delta`
- `premarket_realized_vol`
- `has_premarket`

These are created in [XG_boost_3.py:452](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L452).

### 3. Slot-Level Features

For each of the `26` regular-session bars, the script creates per-slot signals such as:

- `slot_XX_slot_bar_return`
- `slot_XX_slot_path_from_open`
- `slot_XX_slot_path_to_close`
- `slot_XX_slot_volume_share`
- `slot_XX_slot_range`
- `close_hXX`

This gives the model a detailed shape of today's intraday path, not just daily aggregates.

### 4. Rolling Features

The script also adds rolling mean and std features across prior days and prior slot summaries. The helper for this is [add_group_rolling_features()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L349).

Conceptually, these rolling features answer:

- How unusual was today's return vs recent history?
- How unusual was today's realized volatility?
- How unusual was each intraday slot pattern?

## Target Construction

The script builds **next-day** targets by shifting the next trading day's `close_h00..close_h25` path onto the current day row.

That means each training row uses:

- Features from today's session
- Targets from the next session

This is why rows with missing next-trading-day information are dropped before training.

## Model Shape

The most important architectural point is this:

- there are `26` horizons
- there is **one XGBoost model per horizon**
- all horizons share the same feature frame

That happens in [train_full_model_set()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L1173).

Saved model files look like:

```text
models/horizon_00.json
models/horizon_01.json
...
models/horizon_25.json
models/model_manifest.json
```

So when someone says "the XGBoost 3 model," what they usually mean is "the trained bundle of 26 horizon models plus metadata and feature names."

## Base And Fast Refresh

`XG_boost_3.py` has two fixed parameter profiles:

- `BEST_FIXED_VARIANT` at [XG_boost_3.py:37](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L37)
- `FAST_REFRESH_VARIANT` at [XG_boost_3.py:48](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L48)

These support two operational behaviors.

### Base Profile

Purpose:

- stable long-window production bundle

Characteristics:

- trained on the most recent `base_window_months`, default `18`
- validated with expanding walk-forward CV
- promotes to:
  - `base/`
  - `current/`

### Fast Refresh Profile

Purpose:

- faster retrain on recent data for operational updates

Characteristics:

- trained on the most recent `refresh_days`, default `60`
- validated with last-block holdout
- promotes to:
  - `refresh/`
  - `current/`

The base-vs-refresh split is implemented in [train_pipeline()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L1596) and in the production registry path code at [XG_boost_3.py:1985](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L1985).

## Main Modes

The CLI modes are defined in [parse_args()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L127) and dispatched in [main()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L3538).

### `bootstrap`

Trains a fresh long-window base candidate and, if validation passes, promotes it.

Entry point:

- [production_bootstrap()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L2634)

### `refresh`

Trains a short-window refresh candidate and, if validation passes, promotes it.

Entry point:

- [production_refresh()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L2658)

### `predict`

Loads the current promoted bundle and scores the requested as-of date.

Entry point:

- [production_predict()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L2682)

### `cycle`

Tries a refresh first and then runs prediction using the best available `current` bundle.

If refresh fails, prediction still runs with the last promoted current model.

Entry point:

- [production_cycle()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L2695)

### `replay_intraday`

This is the experimental simulation mode.

It walks one replay date through all `26` regular-session cutoffs and compares:

- a frozen static base bundle
- a freshly retrained refresh bundle at each cutoff

Entry point:

- [replay_intraday()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L3246)

## Production Artifact Layout

The production registry defaults to:

```text
artifacts/production_nextday/
```

Important subdirectories:

- `base/` = latest validated long-window bundle
- `refresh/` = latest validated fast-refresh bundle
- `current/` = active promoted bundle used by prediction
- `staging/` = candidate bundles before promotion
- `failed/` = rejected or invalid bundles

Each bundle typically contains:

```text
cv_results.csv
cv_fold_details.csv
feature_names.json
metadata.json
run_summary.json
models/
predictions/
reports/
cycle_status.json
```

## Validation And Safety Checks

Candidate bundles are validated before promotion in [validate_candidate_bundle()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L2230).

Checks include:

- all `26` horizon model files exist
- feature schema is present and non-empty
- manifest horizon count is correct
- smoke predictions have the expected shape
- smoke predictions are finite
- final-horizon distribution is not degenerate
- refresh bundles do not drift from the active feature schema

There is also target cleaning in [sanitize_training_targets()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L2182):

- rows with missing targets are removed
- rows with extreme target magnitudes are removed
- training aborts if too many anomalous rows are dropped

## How Prediction Works

Prediction logic lives in:

- [infer_pipeline()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L1855)
- [run_prediction_bundle()](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L2490)

At inference time the script:

1. loads recent bars
2. rebuilds the feature dataset
3. picks the latest complete origin date
4. aligns features to the saved `feature_names.json`
5. runs all `26` horizon models
6. writes:
   - `predictions/predictions.csv`
   - `predictions/predicted_path.csv`
   - optional plots and markdown reports

## Replay Mode In Plain English

Replay mode exists to answer this question:

"If we had been retraining during the day as more of the session became visible, would the refresh model beat the static base model?"

It does this by:

1. creating cutoff snapshots for each regular-session bar
2. training one static base bundle on historical data
3. training a new refresh bundle at each cutoff using only data available up to that cutoff
4. comparing path RMSE and final-horizon metrics for base vs refresh

This is the part of the script that most directly supports the "base model plus fast refresh" idea.

## Common Misunderstandings

### "It predicts one return"

No. It predicts a next-day **26-step path**.

### "It uses one XGBoost model"

No. It trains and serves **26 horizon models** in a bundle.

### "Refresh updates the current model in place"

No. Refresh trains in `staging/`, validates the candidate, and only then promotes it into `current/`.

### "It consumes partial current-session regular data in production mode"

No. The production dataset is built from complete regular sessions. Replay mode is what simulates cutoff-by-cutoff intraday behavior.

### "The replay model and production model are different pipelines"

They are closely related. Replay uses a cutoff-aware dataset, but the overall target idea, feature family, and multi-horizon model structure are the same.

## Files A New Teammate Should Read First

If someone needs to understand the code quickly, read in this order:

1. [scripts/XG_boost_3.py:404](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L404)
   This shows how the main symbol-day dataset is built.
2. [scripts/XG_boost_3.py:1173](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L1173)
   This shows how the 26-model bundle is trained and saved.
3. [scripts/XG_boost_3.py:1596](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L1596)
   This shows the main training pipeline for base and fast refresh.
4. [scripts/XG_boost_3.py:2490](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L2490)
   This shows how production prediction works.
5. [scripts/XG_boost_3.py:3246](/Volumes/Transcend/COSC471/scripts/XG_boost_3.py#L3246)
   This shows the replay workflow and the base-versus-refresh simulation.

## Recommended Commands

Train a base bundle:

```bash
python3 scripts/XG_boost_3.py \
  --mode bootstrap \
  --device cuda \
  --run-root artifacts/production_nextday \
  --base-window-months 18
```

Train a refresh bundle:

```bash
python3 scripts/XG_boost_3.py \
  --mode refresh \
  --device cuda \
  --run-root artifacts/production_nextday \
  --refresh-days 60
```

Run prediction:

```bash
python3 scripts/XG_boost_3.py \
  --mode predict \
  --device cuda \
  --run-root artifacts/production_nextday \
  --as-of-date 2026-03-18
```

Run intraday replay:

```bash
python3 scripts/XG_boost_3.py \
  --mode replay_intraday \
  --device cuda \
  --start-date 2020-01-01 \
  --end-date 2026-03-03 \
  --replay-date 2026-03-02 \
  --truth-date 2026-03-03 \
  --run-root artifacts/replay_nextday
```

## Bottom Line

If you remember only five things about `XG_boost_3.py`, remember these:

- It predicts the next day's `26` regular-session 15-minute closes, not one scalar return.
- It converts current-day bars into a wide `symbol x trade_date` feature row.
- It trains one XGBoost model per horizon and saves them as a bundle.
- It has two operational profiles: stable base and short-window fast refresh.
- Its replay mode is the place where base vs refresh behavior is tested cutoff by cutoff.
