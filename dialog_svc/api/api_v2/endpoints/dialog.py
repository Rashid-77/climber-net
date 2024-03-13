from typing import Any, List, Optional

import crud
import models
import schemas
from api.deps import get_current_active_user, get_db
from db.tarantool.db import t_session
from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.dialog import dialog_srv
from sqlalchemy.orm import Session
from utils.log import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/{user_id}/create/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.DialogMsgRead,
)
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
    return await dialog_srv.save_dialog_msg(
        db=t_session,
        to_user=user,
        from_user=current_user,
        msg_in=dialog_in,
    )


@router.get("/{user_id}/list/", response_model=List[schemas.DialogMsgRead])
async def list_dialog(
    user_id: int,
    offset: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(10, ge=1, le=20),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get dialog of the current_user with user_id
    """
    user: models.User = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    if user_id == current_user.id:
        raise HTTPException(
            status_code=422,
            detail="Select the user you chatted with",
        )
    if crud.dialog.get_by_users(t_session, user_id, current_user.id) is None:
        return []
    return await dialog_srv.load_dialog_msg_list(
        db=t_session,
        user_a=current_user,
        user_b=user,
        limit=limit,
        offset=offset,
    )
