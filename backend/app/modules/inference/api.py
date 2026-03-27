"""
Inference API endpoints.

Provides stock price prediction using trained XGBoost model.
The response shape depends on ACTIVE_MODEL:
  - stock_prediction_xgb_global  → PredictionResponse
  - nextday_15m_path_final       → NextDayPredictionResponse

Replay endpoints (/inference/replay/*) serve pre-computed predictions from a
replay_intraday simulation and do not require a live DB or feature pipeline.
"""

import math

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.modules.inference.model_loader import replay_bundle
from app.modules.inference.schemas import (
    NextDayBarPrediction,
    NextDayPredictionResponse,
    ReplayStatusResponse,
)
from app.modules.inference.service import InferenceService

router = APIRouter(prefix="/inference", tags=["inference"])


# ── Production endpoint ────────────────────────────────────────────────────────

@router.get("/predict/{symbol}", response_model=NextDayPredictionResponse)
def predict_stock_price(symbol: str, session: SessionDep) -> NextDayPredictionResponse:
    """
    Get next-day 26-bar 15-min path prediction for a stock.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')

    Raises:
        404: Stock not found
        400: Insufficient data or missing features
        500: Model error
    """
    try:
        return InferenceService.predict_stock_price(session, symbol.upper())
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# ── Replay simulation endpoints ────────────────────────────────────────────────

def _require_replay():
    if replay_bundle is None:
        raise HTTPException(
            status_code=503,
            detail="No replay simulation loaded. Run XG_boost_3.py --mode replay_intraday first.",
        )
    return replay_bundle


@router.get("/replay/status", response_model=ReplayStatusResponse)
def replay_status() -> ReplayStatusResponse:
    """Return current bar position in the replay simulation."""
    rb = _require_replay()
    return ReplayStatusResponse(**rb.status())


@router.post("/replay/advance", response_model=ReplayStatusResponse)
def replay_advance() -> ReplayStatusResponse:
    """
    Advance the replay to the next 15-min bar and return the new status.
    Simulates a new bar arriving during the trading session.
    Idempotent at bar 25 (last bar of day).
    """
    rb = _require_replay()
    return ReplayStatusResponse(**rb.advance())


@router.get("/replay/predict/{symbol}", response_model=NextDayPredictionResponse)
def replay_predict(symbol: str) -> NextDayPredictionResponse:
    """
    Return the next-day path prediction for a symbol at the current replay bar.
    Reads from pre-computed CSVs — no DB or feature pipeline required.
    """
    rb = _require_replay()
    try:
        rows = rb.predict_for_symbol(symbol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    cutoff_close = float(rows["cutoff_close"].iloc[0])
    path = [
        NextDayBarPrediction(
            bar_idx=int(r["bar_idx"]),
            bar_time=str(r["bar_time"]),
            pred_close=float(r["pred_close"]),
        )
        for _, r in rows.iterrows()
    ]
    final_price = path[-1].pred_close
    predicted_full_day_return = (final_price / cutoff_close - 1) * 100

    return NextDayPredictionResponse(
        symbol=symbol.upper(),
        current_price=cutoff_close,
        prediction_date=__import__("datetime").datetime.fromisoformat(rb.replay_dir.name),
        predicted_full_day_return=predicted_full_day_return,
        predicted_direction="up" if predicted_full_day_return >= 0 else "down",
        path=path,
        model_version=f"replay_{rb.replay_dir.name}_{rb.slot_name}",
    )
