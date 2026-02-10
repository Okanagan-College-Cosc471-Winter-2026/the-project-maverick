from datetime import datetime

from sqlmodel import Session, select

from app.modules.market.models import Candle


def get_candles(
    session: Session,
    symbol: str,
    start: datetime,
    end: datetime,
) -> list[Candle]:
    statement = (
        select(Candle)
        .where(Candle.symbol == symbol.upper())
        .where(Candle.ts >= start)
        .where(Candle.ts <= end)
        .order_by(Candle.ts)
    )
    return session.exec(statement).all()
