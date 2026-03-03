"""
Model loader for XGBoost stock prediction model.

Implements singleton pattern to load model once on startup.
"""

import json
import logging
from pathlib import Path
from typing import Any, ClassVar

import joblib  # type: ignore[import-untyped]
from xgboost import XGBRegressor

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Singleton class to manage the XGBoost model.

    Loads the model once on first access and caches it for subsequent requests.
    """

    _instance: ClassVar["ModelManager | None"] = None
    _model: XGBRegressor | None = None
    _feature_names: list[str] | None = None
    _metadata: dict[str, Any] | None = None
    _ticker_encoder: Any = None
    _model_path: Path

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize model paths."""
        if self._model is None:
            # Path to model artifacts at the backend/app/models level
            base_path = Path(__file__).parent.parent.parent / "models"
            self._model_path = base_path

    def load_model(self) -> None:
        """Load the XGBoost model and metadata from disk."""
        if self._model is not None:
            return  # Already loaded

        model_file = self._model_path / "xgb_global.pkl"
        metadata_file = self._model_path / "meta.json"
        encoder_file = self._model_path / "encoder.pkl"

        # Check if files exist
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")

        # Load metadata
        with open(metadata_file) as f:
            self._metadata = json.load(f)
            
        # Load feature names from metadata
        self._feature_names = self._metadata.get("feature_cols", [])

        # Load model using joblib (since it was saved with joblib to preserve sklearn wrapper)
        logger.info(f"Loading model from {model_file}...")
        self._model = joblib.load(model_file)

        # Load ticker encoder
        if encoder_file.exists():
            self._ticker_encoder = joblib.load(encoder_file)

        logger.info(f"Model loaded from {self._model_path}")
        logger.info(f"  - Horizon: {self._metadata.get('horizon')} mins")
        logger.info(f"  - Split date: {self._metadata.get('split_date')}")
        if self._ticker_encoder is not None:
            logger.info(
                f"  - Ticker encoder loaded with {len(self._ticker_encoder.classes_)} symbols"
            )

    @property
    def model(self) -> XGBRegressor:
        """Get the loaded model."""
        if self._model is None:
            self.load_model()
        assert self._model is not None
        return self._model

    @property
    def feature_names(self) -> list[str]:
        """Get the feature names."""
        if self._feature_names is None:
            self.load_model()
        assert self._feature_names is not None
        return self._feature_names

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the model metadata."""
        if self._metadata is None:
            self.load_model()
        assert self._metadata is not None
        return self._metadata

    @property
    def ticker_encoder(self) -> Any:
        """Get the ticker encoder."""
        if self._ticker_encoder is None:
            self.load_model()
        return self._ticker_encoder


# Global instance
model_manager = ModelManager()
