from api.api_v2.endpoints import dialog, login
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(dialog.router, prefix="/dialog", tags=["dialog"])
