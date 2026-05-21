from fastapi import APIRouter
from backend.core.config import Config

Core_router = APIRouter(prefix="/info", tags=["Info"])

@Core_router.get("/status")
async def get_status():
    return {"status": "good", "msg": "Пингвины чувствуют себя отлично!"}