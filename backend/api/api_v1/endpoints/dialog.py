from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import crud
import schemas
from api.deps import get_db, get_current_active_user
from services.dialog import dialog_srv
from utils.log import get_logger
logger = get_logger(__name__)

router = APIRouter()


@router.post(
        "/{user_id}/create/", 
        status_code=status.HTTP_201_CREATED, 
        response_model=schemas.DialogMsgRead)
async def create_dialog_msg(
    user_id: int,
    dialog_in: schemas.DialogMsgCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new message in dialog.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    if user_id == current_user.id:
        raise HTTPException(
            status_code=422,
            detail="User can't write to yourself.",
        )
    return await dialog_srv.save_dialog(db, to_user=user, from_user=current_user, msg_in=dialog_in)


@router.get("/{user_id}/list/", response_model=List[schemas.DialogMsgRead])
async def list_dialog(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get dialog of the current_user with user_id
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    return crud.dialog.get_dialog_list(db, from_user=current_user, to_user=user)

