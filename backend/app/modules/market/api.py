from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.modules.market.models import SUPPORTED_TICKERS
from app.modules.market.schemas import CandleRead, StockInfo, STOCK_DIRECTORY
from app.modules.market.service import CandleService

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/stocks", response_model=list[StockInfo])
def list_stocks():
    """List all supported stocks."""
    return [StockInfo(symbol=s, name=STOCK_DIRECTORY[s]) for s in SUPPORTED_TICKERS]


@router.get("/stocks/{symbol}/candles", response_model=list[CandleRead])
def get_candles(
    symbol: str,
    days: int = 30,
    session: SessionDep = None,  # type: ignore[assignment]
):
    """Get 15-min candles for a stock chart."""
    symbol = symbol.upper()
    if symbol not in SUPPORTED_TICKERS:
        raise HTTPException(status_code=404, detail=f"Unsupported ticker: {symbol}")
    return CandleService.get_candles(session, symbol, days)
