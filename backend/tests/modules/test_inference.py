from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient


def test_predict_stock_price(client: TestClient) -> None:
    # Note: Requires DB data which might not be present in unit test environment
    # This might fail with 404 or 500 if DB is empty or model missing
    # We expect 404 for a fake symbol, which validates the endpoint exists
    response = client.get("/api/v1/inference/predict/FAKE_SYMBOL")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_predict_response_includes_confidence(client: TestClient) -> None:
    """Verify that a successful prediction populates the confidence field."""
    mock_features = pd.DataFrame(
        [
            {
                "ticker_id": 0,
                "hour": 0,
                "ret_1": 0.001,
                "ret_5": 0.005,
                "ret_10": 0.01,
                "ret_20": 0.02,
                "dist_sma_10": 0.0,
                "dist_sma_50": 0.0,
                "volatility_20": 0.02,
                "rsi": 50.0,
                "vol_ratio": 1.0,
                "dayofweek": 2,
            }
        ]
    )

    with (
        patch("app.modules.inference.service.crud") as mock_crud,
        patch("app.modules.inference.service.model_manager") as mock_mm,
        patch(
            "app.modules.inference.service.prepare_features_for_prediction",
            return_value=mock_features,
        ),
    ):
        mock_crud.get_stock.return_value = MagicMock(symbol="AAPL")
        mock_crud.get_ohlc.return_value = [
            MagicMock(
                date="2026-02-20",
                open=150,
                high=155,
                low=149,
                close=153,
                volume=1000,
            )
        ] * 60

        mock_mm.model.predict.return_value = np.array([0.01])
        mock_mm.ticker_encoder = MagicMock()
        mock_mm.metadata = {"training_date": "2026-02-11"}

        response = client.get("/api/v1/inference/predict/AAPL")

    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] is not None
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0
