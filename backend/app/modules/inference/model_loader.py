"""
Model loader for XGBoost stock prediction model.

Implements singleton pattern to load model once on startup.
"""

import json
from pathlib import Path
from typing import ClassVar

from xgboost import XGBRegressor


class ModelManager:
    """
    Singleton class to manage the XGBoost model.
    
    Loads the model once on first access and caches it for subsequent requests.
    """
    
    _instance: ClassVar["ModelManager | None"] = None
    _model: XGBRegressor | None = None
    _feature_names: list[str] | None = None
    _metadata: dict | None = None
    _model_path: Path
    
    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize model paths."""
        if self._model is None:
            # Path to model artifacts
            base_path = Path(__file__).parent / "models" / "stock_prediction"
            self._model_path = base_path
    
    def load_model(self) -> None:
        """Load the XGBoost model and metadata from disk."""
        if self._model is not None:
            return  # Already loaded
        
        model_file = self._model_path / "model.json"
        feature_file = self._model_path / "feature_names.json"
        metadata_file = self._model_path / "metadata.json"
        
        # Check if files exist
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")
        
        # Load model
        self._model = XGBRegressor()
        self._model.load_model(str(model_file))
        
        # Load feature names
        with open(feature_file) as f:
            self._feature_names = json.load(f)
        
        # Load metadata
        with open(metadata_file) as f:
            self._metadata = json.load(f)
        
        print(f"✓ Loaded XGBoost model from {model_file}")
        print(f"  - Features: {len(self._feature_names)}")
        print(f"  - Prediction horizon: {self._metadata.get('prediction_horizon')} bars")
        print(f"  - Training date: {self._metadata.get('training_date')}")
    
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
    def metadata(self) -> dict:
        """Get the model metadata."""
        if self._metadata is None:
            self.load_model()
        assert self._metadata is not None
        return self._metadata


# Global instance
model_manager = ModelManager()
