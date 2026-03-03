"""
Market module database queries.
"""

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.market.models import DailyPrice, Stock


def get_active_stocks(session: Session) -> list[Stock]:
    """Return all active stocks, ordered by symbol."""
    stmt = select(Stock).where(Stock.is_active.is_(True)).order_by(Stock.symbol)
    return list(session.scalars(stmt).all())


def get_stock(session: Session, symbol: str) -> Stock | None:
    """Return a single stock by symbol, or None."""
    return session.get(Stock, symbol.upper())


def get_daily_prices(
    session: Session,
    symbol: str,
    start: date,
    end: date,
) -> list[Any]:
    """Return daily OHLC rows for a symbol within a date range."""
    from sqlalchemy import text
    query = text(f"""
        SELECT date::timestamp as date,
               open::numeric as open,
               high::numeric as high,
               low::numeric as low,
               close::numeric as close,
               volume::numeric as volume
        FROM market."{symbol.upper()}"
        WHERE date::timestamp >= :start AND date::timestamp <= :end
        ORDER BY date ASC
    """)
    return list(session.execute(query, {"start": start, "end": end}).fetchall())


def get_ohlc(session: Session, symbol: str, days: int = 365) -> list[Any]:
    """
    Return recent OHLC data for a symbol.

    Args:
        session: Database session
        symbol: Stock symbol
        days: Number of days of history to retrieve (default 365)

    Returns:
        List of DailyPrice-like records, ordered by date ascending
    """
    from sqlalchemy import text
    query = text(f"""
        SELECT date::timestamp as date,
               open::numeric as open,
               high::numeric as high,
               low::numeric as low,
               close::numeric as close,
               volume::numeric as volume
        FROM market."{symbol.upper()}"
        ORDER BY date DESC
        LIMIT :limit
    """)
    # Get results and reverse to have oldest first
    results = session.execute(query, {"limit": days * 30}).fetchall()
    return list(reversed(results))
