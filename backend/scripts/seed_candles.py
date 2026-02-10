import os
import random
from datetime import datetime, timedelta, timezone, time

import psycopg
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

# NYSE market hours (Eastern Time)
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)

# Fixed US market holidays (month, day). Observed dates shift if on weekend,
# but we already skip weekends so this is close enough for synthetic data.
FIXED_HOLIDAYS = {
    (1, 1),    # New Year's Day
    (7, 4),    # Independence Day
    (12, 25),  # Christmas Day
}


def _us_market_holidays(year: int) -> set[datetime]:
    """Return a set of dates for major US market holidays in a given year."""
    holidays: set[datetime] = set()

    # Fixed-date holidays
    for m, d in FIXED_HOLIDAYS:
        holidays.add(datetime(year, m, d))

    # MLK Day: 3rd Monday of January
    holidays.add(_nth_weekday(year, 1, 0, 3))
    # Presidents' Day: 3rd Monday of February
    holidays.add(_nth_weekday(year, 2, 0, 3))
    # Memorial Day: last Monday of May
    holidays.add(_last_weekday(year, 5, 0))
    # Labor Day: 1st Monday of September
    holidays.add(_nth_weekday(year, 9, 0, 1))
    # Thanksgiving: 4th Thursday of November
    holidays.add(_nth_weekday(year, 11, 3, 4))
    # Good Friday (2 days before Easter Sunday)
    holidays.add(_easter(year) - timedelta(days=2))

    return holidays


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> datetime:
    """Return the nth occurrence of weekday (0=Mon) in month/year."""
    first = datetime(year, month, 1)
    day_offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=day_offset + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> datetime:
    """Return the last occurrence of weekday (0=Mon) in month/year."""
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    day_offset = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=day_offset)


def _easter(year: int) -> datetime:
    """Anonymous Gregorian algorithm for Easter Sunday."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return datetime(year, month, day + 1)


def _build_holiday_set(start_year: int, end_year: int) -> set[str]:
    """Build a set of 'YYYY-MM-DD' strings for quick lookup."""
    dates: set[str] = set()
    for y in range(start_year, end_year + 1):
        for dt in _us_market_holidays(y):
            dates.add(dt.strftime("%Y-%m-%d"))
    return dates


def gen_candles(
    symbol: str,
    start: datetime,
    end: datetime,
    start_price: float,
    holidays: set[str],
):
    """
    Generate 15-min synthetic candles only during NYSE trading hours,
    skipping weekends and US market holidays.
    """
    ts = start
    close = start_price

    while ts <= end:
        local = ts.astimezone(ET)

        # Skip weekends
        if local.weekday() >= 5:
            ts += timedelta(minutes=15)
            continue

        # Skip holidays
        if local.strftime("%Y-%m-%d") in holidays:
            ts += timedelta(minutes=15)
            continue

        # Skip outside market hours (last candle starts at 15:45)
        local_time = local.time()
        if local_time < MARKET_OPEN or local_time >= MARKET_CLOSE:
            ts += timedelta(minutes=15)
            continue

        shock = random.gauss(0, 0.001)
        drift = 0.00001
        close = max(0.01, close * (1.0 + drift + shock))
        volume = int(max(0, random.gauss(1_200_000, 300_000)))

        yield (symbol, ts.isoformat(), f"{close:.6f}", str(volume))
        ts += timedelta(minutes=15)


STOCKS = {
    "AAPL": 180.0,
    "MSFT": 420.0,
    "GOOGL": 175.0,
}


def main():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("Set DATABASE_URL env var, e.g. postgresql://user:pass@host:5432/db")

    days = int(os.environ.get("DAYS", "730"))
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(days=days)
    # Align to 15-min boundary
    start = start - timedelta(minutes=start.minute % 15)

    holidays = _build_holiday_set(start.year, end.year)

    with psycopg.connect(dsn) as con:
        with con.cursor() as cur:
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

            for symbol, start_price in STOCKS.items():
                print(f"Seeding {symbol} (start_price=${start_price:.2f}) ...")

                cur.execute("DELETE FROM market.candles_15m WHERE symbol = %s;", (symbol,))

                cur.execute("DROP TABLE IF EXISTS _candles_15m_load;")
                cur.execute("""
                    CREATE TEMP TABLE _candles_15m_load (
                      symbol TEXT,
                      ts     TIMESTAMPTZ,
                      close  NUMERIC(18,6),
                      volume BIGINT
                    ) ON COMMIT DROP;
                """)

                with cur.copy("COPY _candles_15m_load (symbol, ts, close, volume) FROM STDIN WITH (FORMAT csv)") as cp:
                    for row in gen_candles(symbol, start, end, start_price, holidays):
                        cp.write(",".join(row) + "\n")

                cur.execute("""
                    INSERT INTO market.candles_15m (symbol, ts, close, volume)
                    SELECT symbol, ts, close, volume
                    FROM _candles_15m_load
                    ON CONFLICT DO NOTHING;
                """)
                con.commit()

                cur.execute("SELECT COUNT(*) FROM market.candles_15m WHERE symbol = %s;", (symbol,))
                count = cur.fetchone()[0]
                print(f"  {symbol}: {count} rows inserted")

        # Summary
        with con.cursor() as cur:
            cur.execute("SELECT symbol, COUNT(*), MIN(ts), MAX(ts) FROM market.candles_15m GROUP BY symbol ORDER BY symbol;")
            print("\nSummary:")
            for sym, cnt, min_ts, max_ts in cur.fetchall():
                print(f"  {sym}: {cnt} rows | {min_ts} -> {max_ts}")


if __name__ == "__main__":
    main()
