from fastapi import APIRouter

router = APIRouter(prefix="/market", tags=["market"])

@router.get("/stocks/{symbol}/candles")
def get_candles(symbol: str, timeframe: str = "1d"):
    """
    Get OHLCV candles for a stock.
    """
    return {"symbol": symbol, "candles": []}

@router.get("/stocks/{symbol}/features")
def get_features(symbol: str):
    """
    Get features for a stock.
    """
    return {"symbol": symbol, "features": {}}
