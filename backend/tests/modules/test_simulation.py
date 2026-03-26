"""
Tests for the simulation endpoints.

These tests read directly from on-disk pre-computed CSVs — no DB required.
The simulation loader is a module-level singleton so it's loaded once per test session.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Pick a symbol guaranteed to be in the dataset (502 symbols in each step CSV)
_KNOWN_SYMBOL = "AAPL"
_UNKNOWN_SYMBOL = "FAKESYM99"
_BASE_URL = "/api/v1/simulation"


@pytest.fixture(scope="module")
def sim_client():
    """TestClient that does NOT override the DB dep (simulation doesn't use DB)."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# /simulation/session
# ---------------------------------------------------------------------------

class TestSessionInfo:
    def test_returns_200(self, sim_client):
        r = sim_client.get(f"{_BASE_URL}/session")
        assert r.status_code == 200

    def test_schema(self, sim_client):
        data = sim_client.get(f"{_BASE_URL}/session").json()
        assert data["replay_date"] == "2026-03-23"
        assert data["steps_completed"] == 26
        assert len(data["step_labels"]) == 26
        assert data["step_labels"][0] == "09:30"
        assert data["step_labels"][25] == "15:45"
        assert data["warm_trees_per_step"] == 30
        assert data["base_trees"] == 1157


# ---------------------------------------------------------------------------
# /simulation/base/{symbol}
# ---------------------------------------------------------------------------

class TestBaseEndpoint:
    def test_known_symbol_200(self, sim_client):
        r = sim_client.get(f"{_BASE_URL}/base/{_KNOWN_SYMBOL}")
        assert r.status_code == 200

    def test_unknown_symbol_404(self, sim_client):
        r = sim_client.get(f"{_BASE_URL}/base/{_UNKNOWN_SYMBOL}")
        assert r.status_code == 404

    def test_schema(self, sim_client):
        data = sim_client.get(f"{_BASE_URL}/base/{_KNOWN_SYMBOL}").json()
        assert data["symbol"] == _KNOWN_SYMBOL
        assert data["date"] == "2026-03-23"
        assert "effective_as_of_date" in data
        assert "model_id" in data
        assert "predicted_full_day_return" in data
        assert data["predicted_direction"] in ("up", "down")
        assert len(data["bars"]) == 26

    def test_bars_schema(self, sim_client):
        bars = sim_client.get(f"{_BASE_URL}/base/{_KNOWN_SYMBOL}").json()["bars"]
        assert bars[0]["bar_idx"] == 0
        assert bars[0]["bar_time"] == "09:30"
        assert bars[25]["bar_idx"] == 25
        assert bars[25]["bar_time"] == "15:45"
        for bar in bars:
            assert isinstance(bar["pred_log_return"], float)

    def test_case_insensitive(self, sim_client):
        r = sim_client.get(f"{_BASE_URL}/base/{_KNOWN_SYMBOL.lower()}")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# /simulation/step/{symbol}/{step}
# ---------------------------------------------------------------------------

class TestStepEndpoint:
    def test_step_0_200(self, sim_client):
        r = sim_client.get(f"{_BASE_URL}/step/{_KNOWN_SYMBOL}/0")
        assert r.status_code == 200

    def test_step_25_200(self, sim_client):
        r = sim_client.get(f"{_BASE_URL}/step/{_KNOWN_SYMBOL}/25")
        assert r.status_code == 200

    def test_step_out_of_range_400(self, sim_client):
        r = sim_client.get(f"{_BASE_URL}/step/{_KNOWN_SYMBOL}/99")
        assert r.status_code == 400

    def test_unknown_symbol_404(self, sim_client):
        r = sim_client.get(f"{_BASE_URL}/step/{_UNKNOWN_SYMBOL}/0")
        assert r.status_code == 404

    def test_step_0_schema(self, sim_client):
        data = sim_client.get(f"{_BASE_URL}/step/{_KNOWN_SYMBOL}/0").json()
        assert data["symbol"] == _KNOWN_SYMBOL
        assert data["step"] == 0
        assert data["slot_label"] == "09:30"
        assert data["base_trees"] == 1157
        assert data["warm_trees_added"] == 30
        assert data["total_trees"] == 1187
        assert len(data["bars"]) == 26

    def test_step_25_tree_count(self, sim_client):
        data = sim_client.get(f"{_BASE_URL}/step/{_KNOWN_SYMBOL}/25").json()
        assert data["slot_label"] == "15:45"
        assert data["warm_trees_added"] == 780   # 26 * 30
        assert data["total_trees"] == 1937       # 1157 + 780

    def test_tree_count_monotonically_increases(self, sim_client):
        totals = [
            sim_client.get(f"{_BASE_URL}/step/{_KNOWN_SYMBOL}/{i}").json()["total_trees"]
            for i in range(26)
        ]
        assert totals == sorted(totals), "Total tree count should increase with each step"
