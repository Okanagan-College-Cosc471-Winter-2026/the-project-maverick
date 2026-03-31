"""
Truncates ml.market_data_15m and reloads it from the downloaded Parquet file.
Uses COPY for fast bulk insert.
"""
import io
import pandas as pd
import psycopg2
import numpy as np

PARQUET_PATH = "/home/cosc-admin/the-project-maverick/downloaded_file2"
DSN = "host=localhost port=5432 dbname=app user=postgres password=changethis"

# Columns in the order the COPY will insert them (excludes agg_id, slot_count, status, created_at)
COLS = [
    "symbol", "trade_date", "window_ts",
    "open", "high", "low", "close", "volume",
    "lag_close_1", "lag_close_5", "lag_close_10",
    "close_diff_1", "close_diff_5",
    "pct_change_1", "pct_change_5",
    "log_return_1",
    "sma_close_5", "sma_close_10", "sma_close_20", "sma_volume_5",
    "previous_close", "overnight_gap_pct", "overnight_log_return",
    "day_of_week", "hour_of_day", "month_of_year",
    "day_monday", "day_tuesday", "day_wednesday", "day_thursday", "day_friday",
    "quarter_1", "quarter_2", "quarter_3", "quarter_4",
    "hour_early_morning", "hour_mid_morning", "hour_afternoon", "hour_late_afternoon",
    "is_gap_up", "is_gap_down",
]

CHUNK_SIZE = 500_000

print("Reading Parquet...")
df = pd.read_parquet(PARQUET_PATH, columns=COLS)
print(f"  {len(df):,} rows, {len(df.columns)} columns")

# Cast floats to Python float (avoid numpy float32 issues with psycopg2)
float_cols = df.select_dtypes(include="float").columns.tolist()
df[float_cols] = df[float_cols].astype("float64")

# Ensure window_ts is tz-aware string psycopg2 can handle
df["window_ts"] = pd.to_datetime(df["window_ts"], utc=True)

print("Connecting to DB...")
conn = psycopg2.connect(DSN)
conn.autocommit = False
cur = conn.cursor()

print("Truncating ml.market_data_15m...")
cur.execute("TRUNCATE TABLE ml.market_data_15m RESTART IDENTITY;")

print("Loading data in chunks via COPY...")
total = len(df)
loaded = 0

for start in range(0, total, CHUNK_SIZE):
    chunk = df.iloc[start:start + CHUNK_SIZE]

    buf = io.StringIO()
    chunk.to_csv(buf, index=False, header=False, na_rep="\\N")
    buf.seek(0)

    cur.copy_expert(
        f"COPY ml.market_data_15m ({', '.join(COLS)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')",
        buf,
    )
    loaded += len(chunk)
    print(f"  {loaded:,} / {total:,} rows loaded ({loaded*100//total}%)")

print("Committing...")
conn.commit()
cur.close()
conn.close()
print("Done.")
