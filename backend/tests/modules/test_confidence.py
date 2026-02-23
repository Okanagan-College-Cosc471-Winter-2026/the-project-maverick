"""Tests for confidence score calculation."""

import numpy as np
import pandas as pd

from app.modules.inference.confidence import (
    _return_magnitude_factor,
    _rsi_factor,
    _volatility_factor,
    _volume_factor,
    calculate_confidence,
)


def _make_features(
    volatility_20: float = 0.02,
    rsi: float = 50.0,
    vol_ratio: float = 1.0,
    ret_1: float = 0.001,
    ret_5: float = 0.005,
    ret_10: float = 0.01,
    ret_20: float = 0.02,
    ticker_id: int = 0,
    hour: int = 0,
    dayofweek: int = 2,
    dist_sma_10: float = 0.0,
    dist_sma_50: float = 0.0,
) -> pd.DataFrame:
    """Helper to build a single-row features DataFrame."""
    return pd.DataFrame(
        [
            {
                "ticker_id": ticker_id,
                "hour": hour,
                "ret_1": ret_1,
                "ret_5": ret_5,
                "ret_10": ret_10,
                "ret_20": ret_20,
                "dist_sma_10": dist_sma_10,
                "dist_sma_50": dist_sma_50,
                "volatility_20": volatility_20,
                "rsi": rsi,
                "vol_ratio": vol_ratio,
                "dayofweek": dayofweek,
            }
        ]
    )


# ---- Volatility factor ----


class TestVolatilityFactor:
    def test_low_volatility_high_score(self) -> None:
        assert _volatility_factor(0.01) > 0.75

    def test_high_volatility_low_score(self) -> None:
        assert _volatility_factor(0.10) < 0.40

    def test_none_returns_neutral(self) -> None:
        assert _volatility_factor(None) == 0.5

    def test_nan_returns_neutral(self) -> None:
        assert _volatility_factor(float("nan")) == 0.5

    def test_zero_returns_neutral(self) -> None:
        assert _volatility_factor(0.0) == 0.5

    def test_negative_returns_neutral(self) -> None:
        assert _volatility_factor(-0.01) == 0.5

    def test_monotonically_decreasing(self) -> None:
        scores = [_volatility_factor(v) for v in [0.01, 0.03, 0.05, 0.10]]
        assert scores == sorted(scores, reverse=True)


# ---- Return magnitude factor ----


class TestReturnMagnitudeFactor:
    def test_small_return_high_score(self) -> None:
        assert _return_magnitude_factor(0.001, 0.02) > 0.9

    def test_large_return_low_score(self) -> None:
        assert _return_magnitude_factor(0.20, 0.02) < 0.25

    def test_zero_return_perfect_score(self) -> None:
        assert _return_magnitude_factor(0.0, 0.02) == 1.0

    def test_none_volatility_uses_rmse_fallback(self) -> None:
        score = _return_magnitude_factor(0.05, None)
        assert 0.0 < score < 1.0

    def test_nan_return_gives_neutral(self) -> None:
        assert _return_magnitude_factor(float("nan"), 0.02) == 0.5

    def test_negative_return_same_as_positive(self) -> None:
        pos = _return_magnitude_factor(0.05, 0.02)
        neg = _return_magnitude_factor(-0.05, 0.02)
        assert pos == neg


# ---- RSI factor ----


class TestRSIFactor:
    def test_neutral_rsi_full_score(self) -> None:
        assert _rsi_factor(50.0) == 1.0

    def test_rsi_in_ideal_range(self) -> None:
        assert _rsi_factor(45.0) == 1.0
        assert _rsi_factor(55.0) == 1.0

    def test_moderate_overbought(self) -> None:
        score = _rsi_factor(65.0)
        assert 0.7 < score < 1.0

    def test_extreme_overbought(self) -> None:
        assert _rsi_factor(85.0) == 0.3

    def test_extreme_oversold(self) -> None:
        assert _rsi_factor(15.0) == 0.3

    def test_none_returns_neutral(self) -> None:
        assert _rsi_factor(None) == 0.5

    def test_nan_returns_neutral(self) -> None:
        assert _rsi_factor(float("nan")) == 0.5

    def test_symmetric_around_50(self) -> None:
        assert _rsi_factor(30.0) == _rsi_factor(70.0)
        assert _rsi_factor(20.0) == _rsi_factor(80.0)


# ---- Volume factor ----


class TestVolumeFactor:
    def test_normal_volume_perfect_score(self) -> None:
        assert _volume_factor(1.0) == 1.0

    def test_high_volume_lower_score(self) -> None:
        assert _volume_factor(2.5) < 0.3

    def test_low_volume_lower_score(self) -> None:
        assert _volume_factor(0.2) < 0.5

    def test_none_returns_neutral(self) -> None:
        assert _volume_factor(None) == 0.5

    def test_zero_returns_neutral(self) -> None:
        assert _volume_factor(0.0) == 0.5

    def test_symmetric_around_one(self) -> None:
        above = _volume_factor(1.5)
        below = _volume_factor(0.5)
        assert above == below


# ---- Integration: calculate_confidence ----


class TestCalculateConfidence:
    def test_returns_float_between_0_and_1(self) -> None:
        features = _make_features()
        score = calculate_confidence(features, 0.01)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_calm_market_small_prediction_high_confidence(self) -> None:
        features = _make_features(volatility_20=0.01, rsi=50.0, vol_ratio=1.0)
        score = calculate_confidence(features, 0.001)
        assert score > 0.75

    def test_volatile_market_extreme_prediction_low_confidence(self) -> None:
        features = _make_features(volatility_20=0.10, rsi=85.0, vol_ratio=3.0)
        score = calculate_confidence(features, 0.20)
        assert score < 0.40

    def test_nan_features_do_not_crash(self) -> None:
        features = _make_features(
            volatility_20=float("nan"),
            rsi=float("nan"),
            vol_ratio=float("nan"),
        )
        score = calculate_confidence(features, 0.01)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_confidence_decreases_with_volatility(self) -> None:
        low_vol = _make_features(volatility_20=0.01)
        high_vol = _make_features(volatility_20=0.08)
        assert calculate_confidence(low_vol, 0.01) > calculate_confidence(high_vol, 0.01)

    def test_confidence_decreases_with_extreme_prediction(self) -> None:
        features = _make_features()
        small_pred = calculate_confidence(features, 0.005)
        large_pred = calculate_confidence(features, 0.15)
        assert small_pred > large_pred

    def test_confidence_decreases_with_extreme_rsi(self) -> None:
        normal_rsi = _make_features(rsi=50.0)
        extreme_rsi = _make_features(rsi=90.0)
        assert calculate_confidence(normal_rsi, 0.01) > calculate_confidence(
            extreme_rsi, 0.01
        )

    def test_confidence_decreases_with_abnormal_volume(self) -> None:
        normal_vol = _make_features(vol_ratio=1.0)
        high_vol = _make_features(vol_ratio=3.0)
        assert calculate_confidence(normal_vol, 0.01) > calculate_confidence(
            high_vol, 0.01
        )
