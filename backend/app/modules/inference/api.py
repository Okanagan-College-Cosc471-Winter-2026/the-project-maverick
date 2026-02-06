from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/inference", tags=["inference"])

class PredictionRequest(BaseModel):
    symbol: str
    horizon: str = "1d"
    features_override: dict[str, Any] | None = None

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    model_version: str
    predicted_at: datetime

@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Get prediction for a stock.
    """
    return PredictionResponse(
        prediction=150.0,
        confidence=0.85,
        model_version="v1-dummy",
        predicted_at=datetime.utcnow()
    )
