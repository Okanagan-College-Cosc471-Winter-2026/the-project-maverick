"""
Feature engineering for stock prediction inference.

Calculates the exact feature set required by the global XGBoost model.
"""

from typing import Any

import numpy as np
import pandas as pd


def calculate_technical_indicators(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Build the full feature frame for one ticker."""
    frame = df.copy()
    frame["ticker"] = symbol
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values(["ticker", "date"]).reset_index(drop=True)

    for col in ["open", "high", "low", "close", "volume"]:
        frame[col] = frame[col].astype(float)

    grouped = frame.groupby("ticker", group_keys=False)

    frame["ret_1"] = grouped["close"].pct_change(1)
    frame["ret_5"] = grouped["close"].pct_change(5)
    frame["ret_10"] = grouped["close"].pct_change(10)
    frame["ret_20"] = grouped["close"].pct_change(20)
    frame["log_ret_1"] = np.log1p(frame["ret_1"])
    frame["hl_spread"] = (frame["high"] - frame["low"]) / frame["close"].replace(0, np.nan)
    frame["oc_spread"] = (frame["close"] - frame["open"]) / frame["open"].replace(0, np.nan)

    for window in [10, 20, 50, 100]:
        frame[f"sma_{window}"] = grouped["close"].transform(lambda s: s.rolling(window).mean())
        frame[f"ema_{window}"] = grouped["close"].transform(
            lambda s: s.ewm(span=window, adjust=False).mean()
        )
        frame[f"dist_sma_{window}"] = frame["close"] / frame[f"sma_{window}"] - 1.0
        frame[f"dist_ema_{window}"] = frame["close"] / frame[f"ema_{window}"] - 1.0

    frame["ema_12"] = grouped["close"].transform(lambda s: s.ewm(span=12, adjust=False).mean())
    frame["ema_26"] = grouped["close"].transform(lambda s: s.ewm(span=26, adjust=False).mean())
    frame["macd"] = frame["ema_12"] - frame["ema_26"]
    frame["macd_signal"] = grouped["macd"].transform(lambda s: s.ewm(span=9, adjust=False).mean())
    frame["macd_hist"] = frame["macd"] - frame["macd_signal"]

    for window in [10, 20, 60]:
        frame[f"volatility_{window}"] = grouped["ret_1"].transform(lambda s: s.rolling(window).std())
        roll_std = grouped["close"].transform(lambda s: s.rolling(window).std())
        roll_mean = grouped["close"].transform(lambda s: s.rolling(window).mean())
        frame[f"bb_{window}_width"] = (4.0 * roll_std) / roll_mean

    delta = grouped["close"].diff()
    avg_gain = delta.clip(lower=0).groupby(frame["ticker"]).transform(lambda s: s.rolling(14).mean())
    avg_loss = (-delta.clip(upper=0)).groupby(frame["ticker"]).transform(lambda s: s.rolling(14).mean())
    frame["rsi_14"] = 100 - (100 / (1 + avg_gain / avg_loss.replace(0, np.nan)))

    frame["vol_ma_20"] = grouped["volume"].transform(lambda s: s.rolling(20).mean())
    frame["vol_ratio_20"] = frame["volume"] / frame["vol_ma_20"]

    for window in [5, 20, 60]:
        frame[f"vol_change_{window}"] = grouped["volume"].pct_change(window)

    frame["rolling_max_10"] = grouped["high"].transform(lambda s: s.rolling(10).max())
    frame["rolling_min_10"] = grouped["low"].transform(lambda s: s.rolling(10).min())
    frame["dist_roll_max_10"] = frame["close"] / frame["rolling_max_10"] - 1.0
    frame["dist_roll_min_10"] = frame["close"] / frame["rolling_min_10"] - 1.0
    frame["hl_pct"] = (frame["high"] - frame["low"]) / frame["close"] * 100

    return frame


def prepare_features_for_prediction(
    df: pd.DataFrame,
    symbol: str,
    ticker_encoder: Any,
    feature_cols_order: list[str],
) -> pd.DataFrame:
    """Prepare one latest-row feature vector for the prediction model."""
    df_with_features = calculate_technical_indicators(df, symbol)

    try:
        ticker_id = ticker_encoder.transform([symbol])[0]
    except ValueError:
        ticker_id = 0

    df_with_features["ticker_id"] = ticker_id
    latest_features = df_with_features.iloc[[-1]].copy().fillna(0)
    return latest_features[feature_cols_order].astype("float32")
