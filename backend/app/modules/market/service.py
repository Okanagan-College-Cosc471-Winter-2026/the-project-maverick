"""
Market module business logic.

Converts DB rows into chart-friendly response shapes.
"""

import calendar
from datetime import date, timedelta, timezone

from sqlalchemy.orm import Session

from app.modules.market import crud
from app.modules.market.schemas import OHLCRead, StockRead


class MarketService:
    """Stateless service layer for market data."""

    @staticmethod
    def list_stocks(session: Session) -> list[StockRead]:
        """Return all active stocks as API response objects."""
        stocks = crud.get_active_stocks(session)
        return [
            StockRead(
                symbol=s.symbol,
                name=s.name,
                sector=s.sector,
                industry=s.industry,
                exchange=s.exchange,
            )
            for s in stocks
        ]

    @staticmethod
    def get_ohlc(
        session: Session,
        symbol: str,
        days: int = 365,
    ) -> list[OHLCRead]:
        """
        Return daily OHLC data for the last *days* trading days.

        Timestamps are returned as Unix seconds (UTC midnight)
        which is what TradingView Lightweight Charts expects.
        """
        end = date.today()
        start = end - timedelta(days=days)

        rows = crud.get_daily_prices(session, symbol, start, end)

        return [
            OHLCRead(
                time=int(
                    calendar.timegm(r.date.timetuple())
                ),
                open=r.open,
                high=r.high,
                low=r.low,
                close=r.close,
                volume=r.volume,
            )
            for r in rows
        ]
