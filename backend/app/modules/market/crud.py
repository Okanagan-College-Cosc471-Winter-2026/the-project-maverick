"""Market module database queries against market and market_intraday schemas.

The project supports two storage layouts:
- Daily bars in `market.daily_prices` (date-based)
- Intraday bars in `market_intraday.prices_5min` (timestamp-based)

CI/unit tests seed `market.daily_prices`, while some deployments may use intraday
data. The functions below transparently fall back to daily tables when the
intraday table is unavailable.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass
class StockRecord:
    symbol: str
    name: str
    sector: str | None
    industry: str | None
    exchange: str | None


def _has_intraday_prices(session: Session) -> bool:
    row = session.execute(
        text(
            """
            SELECT EXISTS (
              SELECT 1
              FROM information_schema.tables
              WHERE table_schema = 'market_intraday'
                AND table_name = 'prices_5min'
            )
            """
        )
    ).one()
    return bool(row[0])


def get_active_stocks(session: Session) -> list[StockRecord]:
    """Return all active stocks ordered by symbol."""
    rows = session.execute(
        text(
            """
            SELECT symbol, name, sector, industry, exchange
            FROM market.stocks
            WHERE is_active = TRUE
            ORDER BY symbol
            """
        )
    ).fetchall()
    return [
        StockRecord(
            symbol=row.symbol,
            name=row.name,
            sector=row.sector,
            industry=row.industry,
            exchange=row.exchange,
        )
        for row in rows
    ]


def get_stock(session: Session, symbol: str) -> StockRecord | None:
    """Return a single stock by symbol, or None."""
    row = session.execute(
        text(
            """
            SELECT symbol, name, sector, industry, exchange
            FROM market.stocks
            WHERE symbol = :symbol
            LIMIT 1
            """
        ),
        {"symbol": symbol.upper()},
    ).fetchone()
    if row is None:
        return None
    return StockRecord(
        symbol=row.symbol,
        name=row.name,
        sector=row.sector,
        industry=row.industry,
        exchange=row.exchange,
    )


def get_daily_prices(
    session: Session,
    symbol: str,
    start: date,
    end: date,
) -> list[Any]:
    """Return OHLC rows for a symbol within a date range."""
    if _has_intraday_prices(session):
        rows = session.execute(
            text(
                """
                SELECT
                    ts::date AS date,
                    open, high, low, close, volume
                FROM market_intraday.prices_5min
                WHERE symbol = :symbol
                  AND ts::date >= :start
                  AND ts::date <= :end
                ORDER BY ts ASC
                """
            ),
            {"symbol": symbol.upper(), "start": start, "end": end},
        ).fetchall()
    else:
        rows = session.execute(
            text(
                """
                SELECT
                    date AS date,
                    open, high, low, close, volume
                FROM market.daily_prices
                WHERE symbol = :symbol
                  AND date >= :start
                  AND date <= :end
                ORDER BY date ASC
                """
            ),
            {"symbol": symbol.upper(), "start": start, "end": end},
        ).fetchall()
    return list(rows)


def get_coverage(session: Session, symbol: str) -> dict[str, Any]:
    """Return earliest date, latest date, and row count for a symbol."""
    if _has_intraday_prices(session):
        row = session.execute(
            text(
                """
                SELECT
                    MIN(ts)::date AS data_from,
                    MAX(ts)::date AS data_to,
                    COUNT(*) AS rows
                FROM market_intraday.prices_5min
                WHERE symbol = :symbol
                """
            ),
            {"symbol": symbol.upper()},
        ).one()
    else:
        row = session.execute(
            text(
                """
                SELECT
                    MIN(date) AS data_from,
                    MAX(date) AS data_to,
                    COUNT(*) AS rows
                FROM market.daily_prices
                WHERE symbol = :symbol
                """
            ),
            {"symbol": symbol.upper()},
        ).one()
    return {"data_from": row[0], "data_to": row[1], "rows": row[2]}


def get_ohlc(session: Session, symbol: str, days: int = 365) -> list[Any]:
    """
    Return recent OHLC data for a symbol, oldest first.

    Args:
        session: Database session
        symbol: Stock symbol
        days: Number of calendar days of history (default 365)

    Returns:
        List of rows with date, open, high, low, close, volume — ascending by ts
    """
    if _has_intraday_prices(session):
        results = session.execute(
            text(
                """
                SELECT
                    ts::date AS date,
                    open, high, low, close, volume
                FROM market_intraday.prices_5min
                WHERE symbol = :symbol
                  AND ts::date >= (CURRENT_DATE - (:days || ' days')::interval)::date
                ORDER BY ts ASC
                """
            ),
            {"symbol": symbol.upper(), "days": days},
        ).fetchall()
    else:
        results = session.execute(
            text(
                """
                SELECT
                    date AS date,
                    open, high, low, close, volume
                FROM market.daily_prices
                WHERE symbol = :symbol
                  AND date >= (CURRENT_DATE - (:days || ' days')::interval)::date
                ORDER BY date ASC
                """
            ),
            {"symbol": symbol.upper(), "days": days},
        ).fetchall()
    return list(results)
