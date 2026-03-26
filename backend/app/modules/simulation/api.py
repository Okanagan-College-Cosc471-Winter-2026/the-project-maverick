"""
Simulation API endpoints.

Provides a replay/demo mode for 2026-03-23 using pre-computed model artifacts.

Endpoints:
  GET /simulation/session
      → session metadata (step count, timestamps, tree counts)

  GET /simulation/base/{symbol}
      → full 26-bar prediction from base model (trained through 2026-03-20)
         implemented as step_00 predictions (1,157 trees, no warm-refresh)

  GET /simulation/step/{symbol}/{step}
      → prediction from the warm-refreshed model at one 15-min bar (step 0–25)
         each step adds 30 trees trained on real intraday data up to that bar
"""

from fastapi import APIRouter, HTTPException

from app.modules.simulation.schemas import (
    SimBaseResponse,
    SimSessionInfo,
    SimStepResponse,
)
from app.modules.simulation.service import SimulationService

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.get("/session", response_model=SimSessionInfo)
def get_session_info() -> SimSessionInfo:
    """
    Return replay session metadata.
    Use this to populate the frontend's step slider / button labels.
    """
    return SimulationService.session_info()


@router.get("/base/{symbol}", response_model=SimBaseResponse)
def get_base_prediction(symbol: str) -> SimBaseResponse:
    """
    Full-day 26-bar prediction for a symbol using the base model (trained through 2026-03-20).

    This uses step_00 of the warm-refresh replay (base 1,157 trees only — no warm refresh
    applied yet), which is equivalent to running the base model cold on 2026-03-23 open data.

    Args:
        symbol: Stock symbol (e.g. 'AAPL', 'MSFT', 'NVDA')
    """
    try:
        return SimulationService.base_predictions(symbol.upper())
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {e}")


@router.get("/step/{symbol}/{step}", response_model=SimStepResponse)
def get_step_prediction(symbol: str, step: int) -> SimStepResponse:
    """
    Prediction from the warm-refreshed model at one specific 15-min bar (step 0–25).

    Each step appends 30 trees trained on intraday data observed up to that bar:
      step  0 → 09:30  (1,157 + 30 =  1,187 trees)
      step  1 → 09:45  (1,157 + 60 =  1,217 trees)
      …
      step 25 → 15:45  (1,157 + 780 = 1,937 trees)

    Args:
        symbol: Stock symbol (e.g. 'AAPL', 'MSFT', 'NVDA')
        step:   Bar index 0–25 (0 = 09:30, 25 = 15:45)
    """
    try:
        return SimulationService.step_prediction(symbol.upper(), step)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {e}")


@router.get("/ohlc/{symbol}", response_model=list[dict])
def get_simulation_ohlc(
    symbol: str, session: SessionDep = None  # type: ignore[assignment]
) -> list[dict]:
    """
    Fetch real 15-min OHLC bars from PostgreSQL exactly for the simulation date (2026-03-23).
    Used by the simulation UI to plot the real data alongside the predictions.
    """
    from datetime import date
    from app.modules.market import crud
    import calendar

    # The simulation replay date is fixed.
    sim_date = date(2026, 3, 23)

    # Re-use the market crud function that queries the DW
    rows = crud.get_daily_prices(session, symbol.upper(), sim_date, sim_date)

    return [
        {
            "time": int(calendar.timegm(r.date.timetuple())),
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": int(round(float(r.volume))),
        }
        for r in rows
    ]
