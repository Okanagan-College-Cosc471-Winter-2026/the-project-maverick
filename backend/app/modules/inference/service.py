"""
Inference service for stock price predictions.
"""

from datetime import datetime, timedelta

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
        
        # 2. Get recent OHLC data (need at least 60 bars for indicators)
        # For 15-minute data, 60 bars = ~1.5 days
        # Get last 100 bars to be safe
        ohlc_data = crud.get_ohlc(session, symbol, days=10)  # Get 10 days worth
        
        if len(ohlc_data) < 60:
            raise ValueError(f"Insufficient data for {symbol}. Need at least 60 bars, got {len(ohlc_data)}")
        
        # 3. Convert to DataFrame
        df = pd.DataFrame([
            {
                'date': row.date,
                'open': row.open,
                'high': row.high,
                'low': row.low,
                'close': row.close,
                'volume': row.volume
            }
            for row in ohlc_data
        ])
        
        # 4. Prepare features
        try:
            ticker_encoder = model_manager.ticker_encoder
            if ticker_encoder is None:
                raise ValueError("Ticker encoder not loaded")
            features = prepare_features_for_prediction(df, symbol, ticker_encoder)
        except Exception as e:
            raise ValueError(f"Error calculating features: {str(e)}")
        
        # 5. Make prediction
        model = model_manager.model
        predicted_return = float(model.predict(features)[0])
        
        # 6. Calculate predicted price
        current_price = float(df['close'].iloc[-1])
        predicted_price = current_price * (1 + predicted_return)
        
        # 7. Get prediction date (1 day ahead)
        last_date = df['date'].iloc[-1]
        if isinstance(last_date, str):
            last_date = pd.to_datetime(last_date)
        prediction_date = last_date + timedelta(days=1)
        
        # 8. Get model version from metadata
        metadata = model_manager.metadata
        training_date = metadata.get('training_date', 'unknown')
        model_version = f"xgboost-v1-{training_date[:10]}"
        
        return PredictionResponse(
            symbol=symbol,
            current_price=current_price,
            predicted_price=predicted_price,
            predicted_return=predicted_return * 100,  # Convert to percentage
            prediction_date=prediction_date,
            confidence=None,  # TODO: Add confidence calculation
            model_version=model_version
        )
