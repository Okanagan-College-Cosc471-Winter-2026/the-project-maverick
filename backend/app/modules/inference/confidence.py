"""
Confidence score calculation for stock predictions.

Derives a heuristic confidence score (0.0–1.0) from feature values
and predicted return without requiring model retraining.

The score combines four factors:
  - Volatility (35%): lower recent volatility → higher confidence
  - Return magnitude (30%): smaller predictions → higher confidence
  - Volume (20%): normal trading volume → higher confidence
  - RSI (15%): neutral RSI range → higher confidence

Note: This is a heuristic, not a calibrated probability.
"""

import numpy as np
import pandas as pd

# Weights for combining individual factors (sum to 1.0)
_WEIGHTS = {
    "volatility": 0.35,
    "return_magnitude": 0.30,
    "rsi": 0.15,
    "volume": 0.20,
}

# Model's test RMSE from metadata — used as fallback scale for return magnitude
_MODEL_RMSE = 0.114


def calculate_confidence(
    features: pd.DataFrame,
    predicted_return: float,
) -> float:
    """
    Calculate a confidence score for a stock prediction.

    Args:
        features: Single-row DataFrame with model features.
                  Expected columns include: volatility_20, rsi, vol_ratio.
        predicted_return: The model's raw predicted return (decimal, not percentage).

    Returns:
        Confidence score clamped to [0.0, 1.0].
    """
    row = features.iloc[0]

    vol_score = _volatility_factor(row.get("volatility_20", None))
    ret_score = _return_magnitude_factor(predicted_return, row.get("volatility_20", None))
    rsi_score = _rsi_factor(row.get("rsi", None))
    volume_score = _volume_factor(row.get("vol_ratio", None))

    confidence = (
        _WEIGHTS["volatility"] * vol_score
        + _WEIGHTS["return_magnitude"] * ret_score
        + _WEIGHTS["rsi"] * rsi_score
        + _WEIGHTS["volume"] * volume_score
    )

    return float(np.clip(confidence, 0.0, 1.0))


def _volatility_factor(volatility_20: float | None) -> float:
    """
    Lower volatility → higher confidence.

    Uses hyperbolic decay: score = 1 / (1 + k * volatility).
    With k=20, volatility of 0.02 gives ~0.71, 0.05 gives ~0.50.
    """
    if volatility_20 is None or np.isnan(volatility_20) or volatility_20 <= 0:
        return 0.5  # neutral fallback

    k = 20.0
    return 1.0 / (1.0 + k * volatility_20)


def _return_magnitude_factor(
    predicted_return: float,
    volatility_20: float | None,
) -> float:
    """
    Predictions close to zero (relative to volatility/RMSE) are more
    reliable than extreme outlier predictions.

    Uses Gaussian decay: exp(-0.5 * (|return| / reference)^2).
    """
    if predicted_return is None or np.isnan(predicted_return):
        return 0.5

    # Use the larger of volatility and model RMSE as reference scale
    if volatility_20 is not None and not np.isnan(volatility_20) and volatility_20 > 0:
        reference = max(volatility_20, _MODEL_RMSE)
    else:
        reference = _MODEL_RMSE

    ratio = abs(predicted_return) / reference
    return float(np.exp(-0.5 * ratio * ratio))


def _rsi_factor(rsi: float | None) -> float:
    """
    RSI in 40–60 range → full confidence (normal conditions).
    Degrades toward extremes: <20 or >80 → 0.3.

    Piecewise linear:
      - |RSI - 50| <= 10: 1.0
      - |RSI - 50| <= 20: taper to 0.7
      - |RSI - 50| <= 30: taper to 0.4
      - |RSI - 50| > 30:  0.3
    """
    if rsi is None or np.isnan(rsi):
        return 0.5

    rsi = float(np.clip(rsi, 0.0, 100.0))
    deviation = abs(rsi - 50.0)

    if deviation <= 10:
        return 1.0
    elif deviation <= 20:
        return 1.0 - 0.3 * ((deviation - 10) / 10)
    elif deviation <= 30:
        return 0.7 - 0.3 * ((deviation - 20) / 10)
    else:
        return 0.3


def _volume_factor(vol_ratio: float | None) -> float:
    """
    Volume ratio near 1.0 (normal) → high confidence.
    Very high or very low volume → lower confidence.

    Uses Gaussian decay centered at 1.0 with sigma=0.5.
    """
    if vol_ratio is None or np.isnan(vol_ratio) or vol_ratio <= 0:
        return 0.5

    deviation = abs(vol_ratio - 1.0)
    return float(np.exp(-0.5 * (deviation / 0.5) ** 2))
