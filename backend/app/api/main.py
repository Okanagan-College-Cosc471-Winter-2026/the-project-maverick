from fastapi import APIRouter

from app.api import utils
from app.modules.inference import api as inference
from app.modules.market import api as market
from app.modules.data import api as data

api_router = APIRouter()
api_router.include_router(market.router)
api_router.include_router(inference.router)
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
