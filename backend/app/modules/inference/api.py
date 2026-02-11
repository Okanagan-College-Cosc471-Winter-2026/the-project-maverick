"""
Inference API endpoints.

Provides stock price prediction using trained XGBoost model.
"""

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.modules.inference.schemas import PredictionResponse
from app.modules.inference.service import InferenceService

router = APIRouter(prefix="/inference", tags=["inference"])


@router.get("/predict/{symbol}", response_model=PredictionResponse)
def predict_stock_price(symbol: str, session: SessionDep) -> PredictionResponse:
    """
    Get 1-day price prediction for a stock.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')

    Returns:
        Prediction with current price, predicted price, and expected return

    Raises:
        404: Stock not found
        400: Insufficient data for prediction
        500: Model error
    """
    try:
        return InferenceService.predict_stock_price(session, symbol.upper())
    except ValueError as e:
        # Stock not found or insufficient data
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        # Model loading or prediction error
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
