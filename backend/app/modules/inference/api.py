from typing import Any
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/inference", tags=["inference"])


class PredictionRequest(BaseModel):
    symbol: str
    horizon: str = "1d"
    features_override: dict[str, Any] | None = None


class PredictionResponse(BaseModel):
    symbol: str
    prediction: float
    confidence: float
    model_version: str
    predicted_at: datetime
    prediction_target_time: int


HORIZON_HOURS: dict[str, int] = {"1h": 1, "4h": 4, "1d": 24, "1w": 168}


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Get prediction for a stock.
    """
    now = datetime.now(timezone.utc)
    hours = HORIZON_HOURS.get(request.horizon, 24)
    target = now + timedelta(hours=hours)

    return PredictionResponse(
        symbol=request.symbol,
        prediction=150.0,
        confidence=0.85,
        model_version="v1-dummy",
        predicted_at=now,
        prediction_target_time=int(target.timestamp()),
    )
