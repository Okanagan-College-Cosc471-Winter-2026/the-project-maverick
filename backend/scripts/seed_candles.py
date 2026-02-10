import os
import math
import random
from datetime import datetime, timedelta, timezone

import psycopg


def gen_candles(symbol: str, start: datetime, end: datetime, start_price: float = 180.0):
    """
    Generate 15-min synthetic candles: (symbol, ts, close, volume)
    - close: geometric-ish random walk
    - volume: random around a baseline
    """
    ts = start
    close = start_price

    while ts <= end:
        # small drift + noise (kept mild so it looks realistic-ish)
        shock = random.gauss(0, 0.002)     # ~0.2% std per 15m
        drift = 0.00005                    # small upward drift
        close = max(0.01, close * (1.0 + drift + shock))

        volume = int(max(0, random.gauss(1_200_000, 300_000)))

        yield (symbol, ts.isoformat(), f"{close:.6f}", str(volume))
        ts += timedelta(minutes=15)


def main():
    # Example: postgresql://postgres:postgres@localhost:5432/mydb
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("Set DATABASE_URL env var, e.g. postgresql://user:pass@host:5432/db")

    symbol = os.environ.get("SYMBOL", "AAPL")

    # Generate last N days (easy to change)
    days = int(os.environ.get("DAYS", "30"))
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(days=days)

    # Align start to a 15-min boundary
    start = start - timedelta(minutes=start.minute % 15)

    with psycopg.connect(dsn) as con:
        with con.cursor() as cur:
            # Schema + table (minimal)
            cur.execute("CREATE SCHEMA IF NOT EXISTS market;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS market.candles_15m (
                  id     BIGSERIAL PRIMARY KEY,
                  symbol TEXT NOT NULL,
                  ts     TIMESTAMPTZ NOT NULL,
                  close  NUMERIC(18,6) NOT NULL,
                  volume BIGINT NOT NULL,
                  UNIQUE (symbol, ts)
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS candles_15m_symbol_ts_idx
                ON market.candles_15m (symbol, ts);
            """)
            con.commit()

            # Use a temp table to COPY into, then INSERT with ON CONFLICT DO NOTHING.
            # COPY is the efficient bulk loader mechanism.
            cur.execute("DROP TABLE IF EXISTS market._candles_15m_load;")
            cur.execute("""
                CREATE TEMP TABLE market._candles_15m_load (
                  symbol TEXT,
                  ts     TIMESTAMPTZ,
                  close  NUMERIC(18,6),
                  volume BIGINT
                ) ON COMMIT DROP;
            """)

            with cur.copy("COPY market._candles_15m_load (symbol, ts, close, volume) FROM STDIN WITH (FORMAT csv)") as cp:
                for row in gen_candles(symbol, start, end, start_price=180.0):
                    # row is already CSV-ready strings
                    cp.write(",".join(row) + "\n")

            cur.execute("""
                INSERT INTO market.candles_15m (symbol, ts, close, volume)
                SELECT symbol, ts, close, volume
                FROM market._candles_15m_load
                ON CONFLICT DO NOTHING;
            """)
            con.commit()

            # Verify: row count + latest 10 rows
            cur.execute("SELECT COUNT(*) FROM market.candles_15m WHERE symbol = %s;", (symbol,))
            count = cur.fetchone()[0]

            cur.execute("""
                SELECT symbol, ts, close, volume
                FROM market.candles_15m
                WHERE symbol = %s
                ORDER BY ts DESC
                LIMIT 10;
            """, (symbol,))
            rows = cur.fetchall()

    print(f"Inserted/available rows for {symbol}: {count}")
    print("Latest 10 rows:")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
