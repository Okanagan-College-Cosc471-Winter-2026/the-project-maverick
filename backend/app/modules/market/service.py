from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.modules.market import crud
from app.modules.market.schemas import CandleRead

class CandleService:
    @staticmethod
    def get_candles(
        session: Session, 
        symbol: str, 
        days: int = 7
    ) -> list[CandleRead]:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        
        candles = crud.get_candles(session, symbol, start, end)
        
        return [
            CandleRead(
                symbol=c.symbol, 
                ts=c.ts, 
                close=c.close, 
                volume=c.volume
            )
            for c in candles
        ]
