"""
Inference service for stock price predictions.
"""

from datetime import timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.modules.inference.features import prepare_features_for_prediction
from app.modules.inference.model_loader import model_manager
from app.modules.inference.schemas import PredictionResponse
from app.modules.market import crud


class InferenceService:
    """Service for making stock price predictions."""

    @staticmethod
    def predict_stock_price(session: Session, symbol: str) -> PredictionResponse:
        """
        Predict the stock price for the next trading day.

        Args:
            session: Database session
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            PredictionResponse with prediction details

        Raises:
            ValueError: If stock not found or insufficient data
        """
        # 1. Verify stock exists
        stock = crud.get_stock(session, symbol)
        if stock is None:
            raise ValueError(f"Stock not found: {symbol}")

        # 2. Get recent OHLC data (need at least 150 bars for 100-bar SMA/EMA)
        # For 5-minute data, 1 day = 78 bars. Get 10 days worth.
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
            ticker_encoder = model_manager.ticker_encoder
            if ticker_encoder is None:
                raise ValueError("Ticker encoder not loaded")
            features = prepare_features_for_prediction(
                df, symbol, ticker_encoder, model_manager.feature_names
            )
        except Exception as e:
            raise ValueError(f"Error calculating features: {str(e)}")

        # 5. Make prediction
        model = model_manager.model
        predicted_return = float(model.predict(features)[0])

        # 6. Calculate predicted price
        current_price = float(df["close"].iloc[-1])
        predicted_price = current_price * (1 + predicted_return)

        # 7. Get prediction date
        last_date = df["date"].iloc[-1]
        if isinstance(last_date, str):
            last_date = pd.to_datetime(last_date)
        metadata = model_manager.metadata
        horizon = metadata.get("horizon", 78)
        prediction_date = last_date + timedelta(minutes=5 * horizon)

        # 8. Get model version from metadata
        split_date = metadata.get("split_date", "unknown")
        model_version = f"xgboost-v1-{split_date}"

        return PredictionResponse(
            symbol=symbol,
            current_price=current_price,
            predicted_price=predicted_price,
            predicted_return=predicted_return * 100,  # Convert to percentage
            prediction_date=prediction_date,
            confidence=None,  # TODO: Add confidence calculation
            model_version=model_version,
        )
