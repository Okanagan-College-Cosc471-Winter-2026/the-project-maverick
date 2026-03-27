"""
Model loader for XGBoost stock prediction models.

Supports two bundle types:
  - LegacyXGBBundle (stock_prediction_xgb_global): single XGBRegressor → scalar return
  - NextDayPathBundle (nextday_15m_path_final): 26 native boosters → list of log-returns

Additionally provides ReplayBundle for serving pre-computed predictions from a
replay_intraday simulation run (ml/artifacts/replay_nextday/YYYY-MM-DD/).

Switch bundles by setting ACTIVE_MODEL in .env.
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import joblib  # type: ignore[import-untyped]
import pandas as pd
import xgboost

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseModelBundle(ABC):
    """Abstract base for all model bundles."""

    model_type: str
    feature_names: list[str]
    metadata: dict[str, Any]
    model_path: Path

    @abstractmethod
    def predict(self, feature_row: pd.DataFrame) -> Any:
        """Run inference on a single prepared feature row."""
        ...


class LegacyXGBBundle(BaseModelBundle):
    """Bundle for stock_prediction_xgb_global (single XGBRegressor, scalar output)."""

    model_type = "legacy_xgb"

    def __init__(self, path: Path) -> None:
        self.model_path = path

        metadata_file = path / "meta.json"
        with open(metadata_file) as f:
            self.metadata = json.load(f)
        self.feature_names = self.metadata.get("feature_cols", [])

        model_file = path / "xgb_global.pkl"
        logger.info("Loading legacy XGBRegressor from %s …", model_file)
        self._model: xgboost.XGBRegressor = joblib.load(model_file)

        encoder_file = path / "encoder.pkl"
        self.ticker_encoder = joblib.load(encoder_file) if encoder_file.exists() else None

        logger.info(
            "LegacyXGBBundle loaded | horizon=%s | split_date=%s | features=%d | tickers=%s",
            self.metadata.get("horizon"),
            self.metadata.get("split_date"),
            len(self.feature_names),
            len(self.ticker_encoder.classes_) if self.ticker_encoder is not None else "n/a",
        )

    def predict(self, feature_row: pd.DataFrame) -> float:
        return float(self._model.predict(feature_row)[0])


class NextDayPathBundle(BaseModelBundle):
    """Bundle for nextday_15m_path_final (26 native boosters, list[float] output)."""

    model_type = "next_day_path"

    def __init__(self, path: Path) -> None:
        self.model_path = path

        feature_names_file = path / "feature_names.json"
        with open(feature_names_file) as f:
            self.feature_names = json.load(f)

        metadata_file = path / "metadata.json"
        with open(metadata_file) as f:
            self.metadata = json.load(f)

        manifest_file = path / "models" / "model_manifest.json"
        with open(manifest_file) as f:
            manifest = json.load(f)

        # The manifest stores absolute training-environment paths; use local filenames only.
        models_dir = path / "models"
        ordered_keys = sorted(manifest["models"].keys())  # target_h00 … target_h25
        self.boosters: list[xgboost.Booster] = []
        for key in ordered_keys:
            filename = Path(manifest["models"][key]).name  # e.g. "horizon_00.json"
            booster = xgboost.Booster()
            booster.load_model(str(models_dir / filename))
            self.boosters.append(booster)

        logger.info(
            "NextDayPathBundle loaded | horizons=%d | features=%d | path=%s",
            len(self.boosters),
            len(self.feature_names),
            path,
        )

    def predict(self, feature_row: pd.DataFrame) -> list[float]:
        """Return 26 log-return predictions, one per 15-min bar."""
        dmatrix = xgboost.DMatrix(feature_row)
        return [float(booster.predict(dmatrix)[0]) for booster in self.boosters]


def create_model_bundle(path: Path) -> BaseModelBundle:
    """Auto-detect and instantiate the correct bundle type."""
    if (path / "models" / "model_manifest.json").exists():
        return NextDayPathBundle(path)
    elif (path / "xgb_global.pkl").exists():
        return LegacyXGBBundle(path)
    else:
        raise ValueError(f"Unknown model bundle structure at {path}")


# ── Replay bundle ──────────────────────────────────────────────────────────────

class ReplayBundle:
    """
    Serves pre-computed predictions from a replay_intraday simulation run.

    Directory layout expected (produced by XG_boost_3.py --mode replay_intraday):
        ml/artifacts/replay_nextday/YYYY-MM-DD/
            paths/refresh/slot_00_path.csv   ← bar 0 (09:30)
            paths/refresh/slot_01_path.csv
            ...
            paths/refresh/slot_25_path.csv   ← bar 25 (16:00)

    Each CSV has columns: symbol, bar_idx, bar_time, pred_close, cutoff_close, ...
    """

    def __init__(self, replay_date_dir: Path) -> None:
        self.replay_dir = replay_date_dir
        paths_dir = replay_date_dir / "paths" / "refresh"
        self.slot_csvs: list[Path] = sorted(paths_dir.glob("slot_*_path.csv"))
        if not self.slot_csvs:
            raise ValueError(f"No slot path CSVs found in {paths_dir}")
        self.total_slots: int = len(self.slot_csvs)
        self.current_slot: int = 0
        logger.info(
            "ReplayBundle loaded | date=%s | slots=%d",
            replay_date_dir.name,
            self.total_slots,
        )

    @property
    def slot_name(self) -> str:
        return self.slot_csvs[self.current_slot].stem.replace("_path", "")

    def advance(self) -> dict[str, Any]:
        """Step to the next bar. Returns current state after advancing."""
        if self.current_slot < self.total_slots - 1:
            self.current_slot += 1
        return self.status()

    def status(self) -> dict[str, Any]:
        return {
            "slot_index": self.current_slot,
            "slot_name": self.slot_name,
            "total_slots": self.total_slots,
            "replay_date": self.replay_dir.name,
            "at_end": self.current_slot == self.total_slots - 1,
        }

    def predict_for_symbol(self, symbol: str) -> pd.DataFrame:
        """Return 26-row DataFrame (bar_idx, bar_time, pred_close, cutoff_close)."""
        df = pd.read_csv(self.slot_csvs[self.current_slot])
        rows = df[df["symbol"] == symbol.upper()].sort_values("bar_idx").reset_index(drop=True)
        if rows.empty:
            raise ValueError(f"Symbol {symbol} not found in replay slot {self.slot_name}")
        return rows


def _load_replay_bundle() -> "ReplayBundle | None":
    """Load the most recent replay date dir, or None if none exists."""
    replay_root = Path(__file__).resolve().parents[4] / "ml" / "artifacts" / "replay_nextday"
    if not replay_root.exists():
        return None
    date_dirs = sorted(d for d in replay_root.iterdir() if d.is_dir())
    if not date_dirs:
        return None
    try:
        return ReplayBundle(date_dirs[-1])
    except Exception as exc:
        logger.warning("ReplayBundle could not be loaded: %s", exc)
        return None


# ── Module-level singletons ────────────────────────────────────────────────────

# Production model — loaded once at import time.
model_bundle: BaseModelBundle = create_model_bundle(
    Path(__file__).resolve().parents[4] / "model_artifacts" / settings.ACTIVE_MODEL
)

# Replay simulation bundle — None if no replay run exists yet.
replay_bundle: ReplayBundle | None = _load_replay_bundle()
