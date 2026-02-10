from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.market.models import Candle

def get_candles(
    session: Session, 
    symbol: str, 
    start: datetime, 
    end: datetime
) -> list[Candle]:
    statement = (
        select(Candle)
        .where(Candle.symbol == symbol.upper())
        .where(Candle.ts >= start)
        .where(Candle.ts <= end)
        .order_by(Candle.ts)
    )
    return session.scalars(statement).all()
