"""Seed synthetic 15-min candle data into market.candles."""

import random
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import insert, text
from sqlmodel import SQLModel, Session

from app.core.db import engine
from app.modules.market.models import Candle, SUPPORTED_TICKERS

ET = ZoneInfo("America/New_York")
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)

DAYS = 730
START_PRICES = {"AAPL": 180.0, "MSFT": 420.0, "GOOGL": 175.0}

FIXED_HOLIDAYS = {(1, 1), (7, 4), (12, 25)}


# ---------------------------------------------------------------------------
# Holiday helpers
# ---------------------------------------------------------------------------

def _nth_weekday(year: int, month: int, weekday: int, n: int) -> datetime:
    first = datetime(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> datetime:
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    return last_day - timedelta(days=(last_day.weekday() - weekday) % 7)


def _easter(year: int) -> datetime:
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    month, day = divmod(h + el - 7 * m + 114, 31)
    return datetime(year, month, day + 1)


def _build_holidays(start_year: int, end_year: int) -> set[str]:
    dates: set[str] = set()
    for y in range(start_year, end_year + 1):
        for m, d in FIXED_HOLIDAYS:
            dates.add(f"{y}-{m:02d}-{d:02d}")
        dates.add(_nth_weekday(y, 1, 0, 3).strftime("%Y-%m-%d"))   # MLK
        dates.add(_nth_weekday(y, 2, 0, 3).strftime("%Y-%m-%d"))   # Presidents
        dates.add(_last_weekday(y, 5, 0).strftime("%Y-%m-%d"))     # Memorial
        dates.add(_nth_weekday(y, 9, 0, 1).strftime("%Y-%m-%d"))   # Labor
        dates.add(_nth_weekday(y, 11, 3, 4).strftime("%Y-%m-%d"))  # Thanksgiving
        dates.add((_easter(y) - timedelta(days=2)).strftime("%Y-%m-%d"))  # Good Friday
    return dates


# ---------------------------------------------------------------------------
# Candle generator
# ---------------------------------------------------------------------------

def _gen_candles(
    symbol: str,
    start: datetime,
    end: datetime,
    start_price: float,
    holidays: set[str],
) -> list[dict]:
    rows: list[dict] = []
    ts = start
    close = start_price

    while ts <= end:
        local = ts.astimezone(ET)

        if (
            local.weekday() >= 5
            or local.strftime("%Y-%m-%d") in holidays
            or not (MARKET_OPEN <= local.time() < MARKET_CLOSE)
        ):
            ts += timedelta(minutes=15)
            continue

        close = max(0.01, close * (1.0 + 0.00001 + random.gauss(0, 0.001)))
        volume = int(max(0, random.gauss(1_200_000, 300_000)))
        rows.append({
            "symbol": symbol,
            "ts": ts,
            "close": round(close, 6),
            "volume": volume,
        })
        ts += timedelta(minutes=15)

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(days=DAYS)
    start -= timedelta(minutes=start.minute % 15)

    holidays = _build_holidays(start.year, end.year)

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS market"))
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.execute(text("TRUNCATE market.candles"))

        for ticker in SUPPORTED_TICKERS:
            price = START_PRICES[ticker]
            print(f"Seeding {ticker} (${price:.2f}) ...")

            rows = _gen_candles(ticker, start, end, price, holidays)
            session.execute(insert(Candle), rows)
            print(f"  {len(rows)} rows")

        session.commit()

    print("\nDone.")


if __name__ == "__main__":
    main()
