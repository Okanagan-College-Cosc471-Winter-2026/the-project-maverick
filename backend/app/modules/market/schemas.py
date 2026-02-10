from datetime import datetime

from pydantic import BaseModel


class CandleRead(BaseModel):
    symbol: str
    ts: datetime
    close: float
    volume: int


class StockInfo(BaseModel):
    symbol: str
    name: str


STOCK_DIRECTORY: dict[str, str] = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc.",
}
