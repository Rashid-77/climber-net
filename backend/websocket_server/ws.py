import json
import os
from typing import Dict

import uvicorn

from aio_pika import IncomingMessage, ExchangeType
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi import WebSocket, WebSocketException, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from queue_r.queue_rabmq import RabbitQueue
from services.friend import friend_cache
# from jose import JWTError
# from pydantic import ValidationError
# from sqlalchemy.orm import Session
from utils import get_settings

# import crud

# from api.deps import get_db
# from utils.security import decode_access_token 

from utils.log import get_logger

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
            pass

    async def send_personal_message(self, message: str, user_id):
        try:
            websocket: WebSocket = self.active_connections[str(user_id)]
            await websocket.send_text(message)
        except KeyError:
            logger.debug(f'{ws_id=} KeyError {user_id=}')
            pass
    
    def get_connected_users(self) -> list:
        return list(map(int, list(self.active_connections.keys())))


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
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
