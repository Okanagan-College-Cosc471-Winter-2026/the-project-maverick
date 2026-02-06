from fastapi import APIRouter

from app.modules.market import api as market
from app.modules.inference import api as inference

api_router = APIRouter()
api_router.include_router(market.router)
api_router.include_router(inference.router)
