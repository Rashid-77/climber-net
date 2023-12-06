from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import WebSocket, WebSocketException, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

import crud

from api.deps import get_db
from utils.log import get_logger
from utils.security import decode_access_token 


logger = get_logger(__name__)

router = APIRouter()


async def get_token(websocket: WebSocket):
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")
    return await oauth2_scheme(websocket)


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket, 
    db: Session = Depends(get_db), 
    token: str = Depends(get_token)
    ):
    try:
        logger.debug(f'  {token=}')
        payload = decode_access_token(token)
        logger.debug(f'  {payload=}')
        user_id: str = payload.get("sub")
    except (JWTError, ValidationError):
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad param")
    
    user = crud.user.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    
    if not crud.user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    await websocket.accept()
    logger.info(f'websocket connection accepted with user {user_id}')
    
    while True:
        data = await websocket.receive_text()
        logger.info(f'  {data=}')
        await websocket.send_text(f"user {user_id} says: {data}")
