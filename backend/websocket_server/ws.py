import os
from typing import List
import uvicorn

from aio_pika import connect, IncomingMessage
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi import WebSocket, WebSocketException, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
# from jose import JWTError
# from pydantic import ValidationError
# from sqlalchemy.orm import Session
# from utils import get_settings

# import crud

# from api.deps import get_db
# from utils.security import decode_access_token 

import logging 

logging.basicConfig(
    filename="log.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname).1s %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
    )


app = FastAPI()
port = os.getenv("WS_PORT", "8090")
router = APIRouter()


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
    logging.info("")
    logging.info(f"Hi {client_id}")
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
        logging.info(f" Buy {client_id}")


@app.get("/health")
async def health():
    logging.info('/health')
    logging.info("")
    return {
        "health": "OK",
    }


if __name__ == "__main__":
    logging.info(f'ws at {port=}')
    uvicorn.run(app, host="0.0.0.0", port=int(port))
    logging.info('exit ws')
