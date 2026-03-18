"""
Inference service for stock price predictions.
"""

import math
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.modules.inference.features import (
    prepare_features_for_next_day,
    prepare_features_for_prediction,
)
from app.modules.inference.model_loader import NextDayPathBundle, model_bundle
from app.modules.inference.schemas import (
    NextDayBarPrediction,
    NextDayPredictionResponse,
    PredictionResponse,
)
from app.modules.market import crud

# 15-min bar start times for a standard 09:30–16:00 session (26 bars)
_BAR_TIMES = [
    f"{9 + (30 + i * 15) // 60:02d}:{(30 + i * 15) % 60:02d}" for i in range(26)
]


class InferenceService:
    """Service for making stock price predictions."""

    @staticmethod
    def predict_stock_price(
        session: Session, symbol: str
    ) -> PredictionResponse | NextDayPredictionResponse:
        """
        Dispatch to the appropriate predictor based on the active model bundle.

        Returns:
            PredictionResponse for the legacy bundle,
            NextDayPredictionResponse for the next-day path bundle.
        """
        if isinstance(model_bundle, NextDayPathBundle):
            return InferenceService._predict_next_day_path(session, symbol)
        return InferenceService._predict_single(session, symbol)

    # ------------------------------------------------------------------
    # Legacy single-horizon predictor
    # ------------------------------------------------------------------

    @staticmethod
    def _predict_single(session: Session, symbol: str) -> PredictionResponse:
        """Predict a single end-of-horizon price using the legacy XGBRegressor."""
        # 1. Verify stock exists
        stock = crud.get_stock(session, symbol)
        if stock is None:
            raise ValueError(f"Stock not found: {symbol}")

        # 2. Get recent OHLC data (need at least 150 bars for 100-bar SMA/EMA)
        ohlc_data = crud.get_ohlc(session, symbol, days=10)
        if len(ohlc_data) < 150:
            raise ValueError(
                f"Insufficient data for {symbol}. Need at least 150 bars, got {len(ohlc_data)}"
            )

        # 3. Convert to DataFrame
        df = pd.DataFrame(
            [
                {
                    "date": row.date,
                    "open": row.open,
                    "high": row.high,
                    "low": row.low,
                    "close": row.close,
                    "volume": row.volume,
                }
                for row in ohlc_data
            ]
        )

        # 4. Prepare features
        try:
            ticker_encoder = model_bundle.ticker_encoder  # type: ignore[attr-defined]
            if ticker_encoder is None:
                raise ValueError("Ticker encoder not loaded")
            features = prepare_features_for_prediction(
                df, symbol, ticker_encoder, model_bundle.feature_names
            )
        except Exception as e:
            raise ValueError(f"Error calculating features: {str(e)}")

        # 5. Make prediction
        predicted_return = model_bundle.predict(features)  # float

        # 6. Calculate predicted price
        current_price = float(df["close"].iloc[-1])
        predicted_price = current_price * (1 + predicted_return)

        # 7. Get prediction date
        last_date = df["date"].iloc[-1]
        if isinstance(last_date, str):
            last_date = pd.to_datetime(last_date)
        horizon = model_bundle.metadata.get("horizon", 78)
        prediction_date = last_date + timedelta(minutes=5 * horizon)

        # 8. Model version
        split_date = model_bundle.metadata.get("split_date", "unknown")
        model_version = f"xgboost-v1-{split_date}"

        return PredictionResponse(
            symbol=symbol,
            current_price=current_price,
            predicted_price=predicted_price,
            predicted_return=predicted_return * 100,
            prediction_date=prediction_date,
            confidence=None,
            model_version=model_version,
        )

    # ------------------------------------------------------------------
    # Next-day path predictor
    # ------------------------------------------------------------------

    @staticmethod
    def _predict_next_day_path(session: Session, symbol: str) -> NextDayPredictionResponse:
        """
        Predict the full next-day 15-min price path using NextDayPathBundle.

        NOTE: Feature engineering for this model (daily aggregates, premarket data,
        intraday slot statistics) is a separate implementation task.  Until that
        pipeline exists, this method will raise a KeyError listing missing columns.
        """
        # 1. Verify stock exists
        stock = crud.get_stock(session, symbol)
        if stock is None:
            raise ValueError(f"Stock not found: {symbol}")

        # 2. Fetch data — placeholder; real aggregation pipeline is a follow-on task
        ohlc_data = crud.get_ohlc(session, symbol, days=10)
        if not ohlc_data:
            raise ValueError(f"No OHLC data available for {symbol}")

        df = pd.DataFrame(
            [
                {
                    "date": row.date,
                    "open": row.open,
                    "high": row.high,
                    "low": row.low,
                    "close": row.close,
                    "volume": row.volume,
                }
                for row in ohlc_data
            ]
        )

        current_price = float(df["close"].iloc[-1])

        # 3. Prepare features (will raise KeyError until aggregation pipeline exists)
        features = prepare_features_for_next_day(df, model_bundle.feature_names)

        # 4. Predict 26 log-returns
        log_returns: list[float] = model_bundle.predict(features)

        # 5. Convert log-returns to absolute prices
        path: list[NextDayBarPrediction] = [
            NextDayBarPrediction(
                bar_idx=i,
                bar_time=_BAR_TIMES[i],
                pred_close=current_price * math.exp(lr),
            )
            for i, lr in enumerate(log_returns)
        ]

        # 6. Full-day return from last bar vs current price
        final_price = path[-1].pred_close
        predicted_full_day_return = (final_price / current_price - 1) * 100

        # 7. Prediction date: next calendar day (follow-on task can make this smarter)
        last_date = df["date"].iloc[-1]
        if isinstance(last_date, str):
            last_date = pd.to_datetime(last_date)
        prediction_date = last_date + timedelta(days=1)
        if isinstance(prediction_date, pd.Timestamp):
            prediction_date = prediction_date.to_pydatetime()

        model_version = model_bundle.metadata.get("model_version", "nextday_15m_path_final")

        return NextDayPredictionResponse(
            symbol=symbol,
            current_price=current_price,
            prediction_date=prediction_date,
            predicted_full_day_return=predicted_full_day_return,
            predicted_direction="up" if predicted_full_day_return >= 0 else "down",
            path=path,
            model_version=model_version,
        )
