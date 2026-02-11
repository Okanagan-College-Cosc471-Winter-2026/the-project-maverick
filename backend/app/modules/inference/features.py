"""
Feature engineering for stock prediction inference.

Ports the technical indicators from ml/features/technical_indicators.py
to work with pandas DataFrames in the backend.
"""

import pandas as pd
import numpy as np


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators needed for model inference.
    
    Args:
        df: DataFrame with columns: date, open, high, low, close, volume
        
    Returns:
        DataFrame with all 17 features required by the model
    """
    result = df.copy()
    
    # Ensure date is datetime and sorted
    result['date'] = pd.to_datetime(result['date'])
    result = result.sort_values('date').reset_index(drop=True)
    
    # 1. Simple Moving Averages
    for window in [10, 20, 50]:
        sma_col = f'sma_{window}'
        dist_col = f'dist_sma_{window}'
        result[sma_col] = result['close'].rolling(window=window).mean()
        result[dist_col] = (result['close'] / result[sma_col]) - 1
    
    # 2. RSI (Relative Strength Index)
    delta = result['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-8)
    result['rsi'] = 100 - (100 / (1 + rs))
    
    # 3. MACD
    ema_fast = result['close'].ewm(span=12, adjust=False).mean()
    ema_slow = result['close'].ewm(span=26, adjust=False).mean()
    result['macd'] = ema_fast - ema_slow
    result['macd_signal'] = result['macd'].ewm(span=9, adjust=False).mean()
    result['macd_diff'] = result['macd'] - result['macd_signal']
    
    # 4. Bollinger Bands
    sma_20 = result['close'].rolling(window=20).mean()
    std_20 = result['close'].rolling(window=20).std()
    result['bb_upper'] = sma_20 + (std_20 * 2.0)
    result['bb_lower'] = sma_20 - (std_20 * 2.0)
    result['bb_width'] = (result['bb_upper'] - result['bb_lower']) / sma_20
    result['bb_position'] = (result['close'] - result['bb_lower']) / (result['bb_upper'] - result['bb_lower'] + 1e-8)
    
    # 5. Lagged Returns
    for lag in [1, 5, 10, 20]:
        result[f'ret_{lag}'] = result['close'].pct_change(lag)
    
    # 6. Volatility
    returns = result['close'].pct_change()
    result['volatility_20'] = returns.rolling(window=20).std()
    
    # 7. Volume Features
    result['vol_ma_20'] = result['volume'].rolling(window=20).mean()
    result['vol_ratio'] = result['volume'] / (result['vol_ma_20'] + 1)
    
    # 8. Time Features
    result['dayofweek'] = result['date'].dt.dayofweek
    result['month'] = result['date'].dt.month
    
    return result


def get_feature_columns() -> list[str]:
    """
    Get the exact list of feature columns used by the model.
    Must match the training feature order exactly.
    
    Returns:
        List of 17 feature column names
    """
    return [
        'ret_1', 'ret_5', 'ret_10', 'ret_20',
        'dist_sma_10', 'dist_sma_20', 'dist_sma_50',
        'rsi', 'macd', 'macd_signal', 'macd_diff',
        'bb_width', 'bb_position',
        'volatility_20',
        'vol_ratio',
        'dayofweek', 'month'
    ]


def prepare_features_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare features for a single prediction.
    
    Args:
        df: DataFrame with recent OHLCV data (at least 60 rows for indicators)
        
    Returns:
        DataFrame with features for the most recent data point
    """
    # Calculate all indicators
    df_with_features = calculate_technical_indicators(df)
    
    # Drop rows with NaN (from rolling windows)
    df_with_features = df_with_features.dropna()
    
    if len(df_with_features) == 0:
        raise ValueError("Insufficient data to calculate features")
    
    # Get only the feature columns in the correct order
    feature_cols = get_feature_columns()
    
    # Return only the most recent row with features
    return df_with_features[feature_cols].iloc[[-1]]
