"""
Pipeline Ops API
================

Endpoints for monitoring the NIBI training pipeline from the Streamlit dashboard.

  GET /ops/pipeline/status   — current job, usage history, active model, SSH ping
  GET /ops/pipeline/usage    — full usage meter history (all runs)
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/ops", tags=["ops"])

# Paths — set via env vars so they work both in Docker and locally.
PIPELINE_LOGS_DIR = Path(os.getenv("PIPELINE_LOGS_DIR", "/data/pipeline_logs"))
MODEL_ARTIFACTS_DIR = Path(os.getenv("MODEL_ARTIFACTS_DIR", "/model_artifacts"))
NIBI_USER = os.getenv("NIBI_USER", "harshsaw")
NIBI_HOST = os.getenv("NIBI_HOST", "nibi.sharcnet.ca")
NIBI_KEY  = Path(os.getenv("NIBI_SSH_KEY", "/root/.ssh/nibi_key"))


def _read_current_job() -> dict | None:
    """Read the most recent nibi_job_YYYY-MM-DD.json, sorted by date descending."""
    if not PIPELINE_LOGS_DIR.exists():
        return None
    records = sorted(PIPELINE_LOGS_DIR.glob("nibi_job_*.json"), reverse=True)
    if not records:
        return None
    try:
        return json.loads(records[0].read_text())
    except Exception:
        return None


def _read_usage_history(limit: int = 30) -> list[dict]:
    """Read last `limit` records from nibi_usage_meter.jsonl."""
    meter = PIPELINE_LOGS_DIR / "nibi_usage_meter.jsonl"
    if not meter.exists():
        return []
    lines = meter.read_text().strip().splitlines()
    records = []
    for line in reversed(lines):
        try:
            records.append(json.loads(line))
        except Exception:
            continue
        if len(records) >= limit:
            break
    return records


def _active_model_info() -> dict:
    """Read the current_base symlink target and its metadata.json if present."""
    symlink = MODEL_ARTIFACTS_DIR / "current_base"
    if not symlink.exists():
        return {"status": "no_model"}
    target = symlink.resolve()
    info: dict = {
        "status": "ok",
        "bundle": target.name,
        "path": str(target),
    }
    meta = target / "metadata.json"
    if meta.exists():
        try:
            m = json.loads(meta.read_text())
            info["train_end_date"] = m.get("train_end_date")
            info["n_estimators"] = m.get("n_estimators")
            info["promoted_at"] = m.get("promoted_at")
        except Exception:
            pass
    return info


def _ssh_ping() -> str:
    """Quick SSH reachability check. Returns 'ok' or 'unreachable'."""
    if not NIBI_KEY.exists():
        return "no_key"
    try:
        r = subprocess.run(
            [
                "ssh", "-i", str(NIBI_KEY),
                "-o", "BatchMode=yes",
                "-o", "ConnectTimeout=8",
                "-o", "StrictHostKeyChecking=accept-new",
                "-o", "ControlMaster=no",
                f"{NIBI_USER}@{NIBI_HOST}",
                "echo pong",
            ],
            capture_output=True, text=True, timeout=12,
        )
        return "ok" if r.returncode == 0 else "unreachable"
    except Exception:
        return "unreachable"


def _elapsed_label(submitted_at: str | None, completed_at: str | None = None) -> str | None:
    """Human-readable elapsed time from submitted_at to now (or completed_at)."""
    if not submitted_at:
        return None
    try:
        start = datetime.fromisoformat(submitted_at).replace(tzinfo=timezone.utc)
        end = (
            datetime.fromisoformat(completed_at).replace(tzinfo=timezone.utc)
            if completed_at
            else datetime.now(timezone.utc)
        )
        secs = int((end - start).total_seconds())
        h, rem = divmod(secs, 3600)
        m, s = divmod(rem, 60)
        return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
    except Exception:
        return None


@router.get("/pipeline/status")
def get_pipeline_status() -> dict:
    """
    Full pipeline status snapshot for the dashboard.

    Returns:
      ssh_status      — "ok" | "unreachable" | "no_key"
      current_job     — most recent nibi_job_*.json content + elapsed label
      usage_history   — last 20 usage meter records
      active_model    — current_base symlink info
      fetched_at      — UTC timestamp of this response
    """
    job = _read_current_job()
    if job:
        job["elapsed"] = _elapsed_label(
            job.get("submitted_at"),
            job.get("completed_at") if job.get("status") == "completed" else None,
        )

    return {
        "ssh_status":    _ssh_ping(),
        "current_job":   job,
        "usage_history": _read_usage_history(20),
        "active_model":  _active_model_info(),
        "fetched_at":    datetime.now(timezone.utc).isoformat(),
    }


@router.get("/pipeline/usage")
def get_pipeline_usage() -> list[dict]:
    """Full usage meter history (all records, newest first)."""
    return _read_usage_history(limit=500)
