import json
import os
import uvicorn
from typing import Dict

from aio_pika import IncomingMessage, ExchangeType
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi import WebSocket, WebSocketException, WebSocketDisconnect
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from queue_r.queue_rabmq import RabbitQueue

import crud
import models
from api.deps import get_db
from services.friend import friend_cache
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from utils import get_settings
from utils.log import get_logger
from utils.security import decode_access_token


port = os.getenv("WS_PORT", 8090)
ws_id = os.getenv("WS_ID", 0)
queue_post = RabbitQueue(url = "amqp://guest:guest@rabbitmq/")
logger = get_logger(f'{__name__} {ws_id}')


async def on_message(message: IncomingMessage):
    d = json.loads(message.body.decode("utf-8"))
    post_author_id = d["wall_user_id"]
    post = d["content"]
    logger.info(f'{post_author_id}, {post}')
    connected = manager.get_connected_users()
    logger.info(f' {connected=}')
    for fr_id in await friend_cache.get_my_friends(post_author_id):
        if fr_id in connected:
            await manager.send_personal_message(f'{post}', fr_id)
            logger.info(f' {fr_id=}, msg_sent')
    # await message.ack() # TODO uncomment it


async def lifespan(app: FastAPI):
    logger.info(f'{ws_id=}, start App')
    await queue_post.connect()
    await queue_post.declare_exchange("post_ex", ExchangeType.FANOUT)
    queue_ws = await queue_post.declare_queue(f"post_q:{ws_id}")
    await queue_ws.bind(queue_post.exchange)
    await queue_ws.consume(on_message, no_ack = True)
    tops = await friend_cache.get_popular_users()
    logger.info(f'{tops=}')
    for t in tops:
        f = await friend_cache.get_my_friends(t)
        logger.info(f'top={t}, {f}')
    yield
    await queue_post.close()
    logger.info(f'{ws_id=}, stop App')


app = FastAPI(lifespan=lifespan)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket] = {}

    async def connect(self, user_id, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[str(user_id)] = websocket
        await self.send_personal_message(f"You are online", user_id)

    def disconnect(self, user_id):
        try:
            self.active_connections.pop(str(user_id))
        except KeyError:
            logger.debug(f'{ws_id=} KeyError {user_id=}')

    async def send_personal_message(self, message: str, user_id):
        try:
            websocket: WebSocket = self.active_connections[str(user_id)]
            await websocket.send_text(message)
        except KeyError:
            logger.debug(f'{ws_id=} KeyError {user_id=}')
    
    def get_connected_users(self) -> list:
        return list(map(int, list(self.active_connections.keys())))


manager = ConnectionManager()

async def api_key_header(websocket: WebSocket):
    api_key_header = APIKeyHeader(name="secret")
    return await api_key_header(websocket)


async def authenticate_user(
        db: Session = Depends(get_db), 
        token: str = Depends(api_key_header)
    ):
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    except (JWTError, ValidationError) as e:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    user = crud.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    client_id: int, 
    user: models.User = Depends(authenticate_user)
    ):
    if client_id != user.id:
        logger.info(f"{client_id} != {user.id}")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    logger.info(f"Hi {client_id}")
    await manager.connect(client_id, websocket)
    # await manager.send_personal_message(f"you connected", client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f" Buy {client_id}")


@app.get("/health")
async def health():
    logger.info('/health')
    return {
        "health": "OK",
    }


if __name__ == "__main__":
    logger.info(f'{ws_id=}, at {port=}')
    uvicorn.run("ws:app", host="0.0.0.0", port=int(port), reload=True)
    logger.info('{ws_id=}, exit')
