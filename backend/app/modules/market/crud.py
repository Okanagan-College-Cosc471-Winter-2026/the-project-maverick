"""
Market module database queries.
"""

from datetime import date

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
) -> list[DailyPrice]:
    """Return daily OHLC rows for a symbol within a date range."""
    stmt = (
        select(DailyPrice)
        .where(DailyPrice.symbol == symbol.upper())
        .where(DailyPrice.date >= start)
        .where(DailyPrice.date <= end)
        .order_by(DailyPrice.date)
    )
    return list(session.scalars(stmt).all())
