"""
Feature engineering for stock prediction inference.

Calculates the exact 53 features used by the XGBoost global model.
"""

from typing import Any

import numpy as np
import pandas as pd


def calculate_technical_indicators(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Calculate all technical indicators needed for model inference.
    Matches the `create_features` function from the training notebook exactly.

    Args:
        df: DataFrame with columns: date, open, high, low, close, volume
        symbol: The ticker symbol

    Returns:
        DataFrame containing exactly the features expected by the model.
    """
    df = df.copy()
    df['ticker'] = symbol
    
    # Needs to be sorted natively
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(['ticker', 'date']).reset_index(drop=True)
    
    # Cast base cols to float
    for c in ['open', 'high', 'low', 'close', 'volume']:
        df[c] = df[c].astype(float)
        
    g = df.groupby('ticker', group_keys=False)

    df['ret_1']     = g['close'].pct_change(1)
    df['ret_5']     = g['close'].pct_change(5)
    df['ret_10']    = g['close'].pct_change(10)
    df['ret_20']    = g['close'].pct_change(20)
    df['log_ret_1'] = np.log1p(df['ret_1'])
    df['hl_spread'] = (df['high'] - df['low']) / df['close'].replace(0, np.nan)
    df['oc_spread'] = (df['close'] - df['open']) / df['open'].replace(0, np.nan)

    for w in [10, 20, 50, 100]:
        df[f'sma_{w}']      = g['close'].transform(lambda s: s.rolling(w).mean())
        df[f'ema_{w}']      = g['close'].transform(lambda s: s.ewm(span=w, adjust=False).mean())
        df[f'dist_sma_{w}'] = df['close'] / df[f'sma_{w}'] - 1.0
        df[f'dist_ema_{w}'] = df['close'] / df[f'ema_{w}'] - 1.0

    df['ema_12']      = g['close'].transform(lambda s: s.ewm(span=12, adjust=False).mean())
    df['ema_26']      = g['close'].transform(lambda s: s.ewm(span=26, adjust=False).mean())
    df['macd']        = df['ema_12'] - df['ema_26']
    df['macd_signal'] = g['macd'].transform(lambda s: s.ewm(span=9, adjust=False).mean())
    df['macd_hist']   = df['macd'] - df['macd_signal']

    for w in [10, 20, 60]:
        df[f'volatility_{w}'] = g['ret_1'].transform(lambda s: s.rolling(w).std())
        roll_std  = g['close'].transform(lambda s: s.rolling(w).std())
        roll_mean = g['close'].transform(lambda s: s.rolling(w).mean())
        df[f'bb_{w}_width'] = (4.0 * roll_std) / roll_mean

    delta    = g['close'].diff()
    avg_gain = delta.clip(lower=0).groupby(df['ticker']).transform(lambda s: s.rolling(14).mean())
    avg_loss = (-delta.clip(upper=0)).groupby(df['ticker']).transform(lambda s: s.rolling(14).mean())
    df['rsi_14'] = 100 - (100 / (1 + avg_gain / avg_loss.replace(0, np.nan)))

    df['vol_ma_20']    = g['volume'].transform(lambda s: s.rolling(20).mean())
    df['vol_ratio_20'] = df['volume'] / df['vol_ma_20']
    
    for w in [5, 20, 60]:
        df[f'vol_change_{w}'] = g['volume'].pct_change(w)

    df['rolling_max_10']   = g['high'].transform(lambda s: s.rolling(10).max())
    df['rolling_min_10']   = g['low'].transform(lambda s: s.rolling(10).min())
    df['dist_roll_max_10'] = df['close'] / df['rolling_max_10'] - 1.0
    df['dist_roll_min_10'] = df['close'] / df['rolling_min_10'] - 1.0

    # Add hl_pct which might have been directly in notebook before feature func
    df['hl_pct'] = (df['high'] - df['low']) / df['close'] * 100

    return df


def prepare_features_for_prediction(
    df: pd.DataFrame, symbol: str, ticker_encoder: Any, feature_cols_order: list[str]
) -> pd.DataFrame:
    """
    Prepare features for a single prediction based on the trained model.

    Args:
        df: DataFrame with recent OHLCV data (need at least 150 rows for rolling 100s)
        symbol: Stock symbol (e.g., 'AAPL')
        ticker_encoder: LabelEncoder for converting symbols to IDs
        feature_cols_order: The exact list of columns expected by the XGBoost model

    Returns:
        DataFrame with features for the most recent data point
    """
    # Calculate all indicators
    df_with_features = calculate_technical_indicators(df, symbol)

    # Encode ticker ID
    try:
        ticker_id = ticker_encoder.transform([symbol])[0]
    except ValueError:
        # If symbol is entirely unknown to encoder, default to the first class or a generic encoding
        ticker_id = 0
        
    df_with_features['ticker_id'] = ticker_id

    # Get the most recent row with features
    latest_features = df_with_features.iloc[[-1]].copy()

    # Fill any potential NaNs in the final row just in case
    latest_features = latest_features.fillna(0)

    # Return exactly the required columns in the exact trained order
    return latest_features[feature_cols_order].astype('float32')
