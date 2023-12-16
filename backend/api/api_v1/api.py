from fastapi import APIRouter

from api.api_v1.endpoints import friend, login, users, post, dialog
# from websocket_server import ws

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["user"])
api_router.include_router(friend.router, prefix="/friend", tags=["friend"])
api_router.include_router(post.router, prefix="/post", tags=["post"])
api_router.include_router(dialog.router, prefix="/dialog", tags=["dialog"])

# api_router.include_router(ws.router, tags=["ws"])
