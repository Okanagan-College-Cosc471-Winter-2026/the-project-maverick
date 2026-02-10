from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Candle(Base):
    __tablename__ = "candles"
    __table_args__ = {"schema": "market"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(index=True)
    ts: Mapped[datetime] = mapped_column(index=True)
    close: Mapped[float]
    volume: Mapped[int]

# Tickers the system supports — used by seed, API validation, and inference
SUPPORTED_TICKERS: list[str] = ["AAPL", "MSFT", "GOOGL"]
