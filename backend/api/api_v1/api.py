from fastapi import APIRouter

from api.api_v1.endpoints import friend, login, users

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["user"])
api_router.include_router(friend.router, prefix="/friend", tags=["friend"])
