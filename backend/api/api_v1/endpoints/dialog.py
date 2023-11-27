from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import crud
import schemas
from api.deps import get_db, get_current_active_user
from utils.log import get_logger
logger = get_logger(__name__)

router = APIRouter()


@router.post(
        "/{user_id}/create/", 
        status_code=status.HTTP_201_CREATED, 
        response_model=schemas.DialogRead)
async def create_dialog_msg(
    user_id: int,
    dialog_in: schemas.DialogCreate,
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
    return crud.dialog.create(db, obj_in=dialog_in, to_user=user, current_user=current_user)


@router.get("/{user_id}/list/", response_model=List[schemas.DialogRead])
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

