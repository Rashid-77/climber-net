import json
import os
from typing import List
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

logger = get_logger(__name__)
port = os.getenv("WS_PORT", 8090)
ws_id = os.getenv("WS_ID", 0)
queue_post = RabbitQueue(url = "amqp://guest:guest@rabbitmq/")

async def on_message(message: IncomingMessage):
    message = message.body.decode("utf-8")
    logger.info(f'{ws_id=}, new msg=({json.loads(message)})')
    tops = await friend_cache.get_popular_users()
    # await message.ack() # TODO uncomment it


async def lifespan(app: FastAPI):
    logger.info(f'{ws_id=}, start App')
    d = await queue_post.connect()
    d = await queue_post.declare_exchange("post_ex", ExchangeType.FANOUT)
    queue_ws = await queue_post.declare_queue(f"post_q:{ws_id}")
    d = await queue_ws.bind(queue_post.exchange)
    d = await queue_ws.consume(on_message, no_ack = True)
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
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_personal_message(f"You are online", websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    logger.info(f"Hi {client_id}")
    await manager.connect(websocket)
    await manager.broadcast(f"Client #{client_id} connected")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
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
