from datetime import datetime

from sqlmodel import Field, SQLModel


class Candle(SQLModel, table=True):
    __tablename__ = "candles"
    __table_args__ = ({"schema": "market"},)

    id: int | None = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, max_length=10)
    ts: datetime = Field(index=True)
    close: float
    volume: int


# Tickers the system supports — used by seed, API validation, and inference
SUPPORTED_TICKERS: list[str] = ["AAPL", "MSFT", "GOOGL"]
