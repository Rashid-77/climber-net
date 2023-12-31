from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import crud, schemas
from api import deps
from schemas.friend import FriendCreate
from models.friend import FriendshipStatus
from services.friend import friend_srv
router = APIRouter()

# from . import get_logger
# logger = get_logger(__name__)


@router.post("/add/{user_id}", response_model=schemas.Friend)
def add_friend(
    user_id: int,
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add friend by id.
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=422,
            detail="Friend's id and user's id can not be the same.",
        )
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    if friend_srv.is_friend(db, user_id, current_user.id):
        raise HTTPException(
            status_code=422,
            detail="User is friend allready.",
        )
    friend = crud.friend.create(
        db, 
        obj_in=FriendCreate(
            user_a=min(user_id, current_user.id), 
            user_b=max(user_id, current_user.id), 
            status=FriendshipStatus.ACCEPTED
            )
        )
    return friend


@router.delete("/delete/{user_id}", response_model=List[schemas.Friend])
def delete_friend_by_id(
    friend_id: int,
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Delete friend by id.
    """
    friend = crud.friend.remove(db, user_id=current_user.id, friend_id=friend_id)
    if not len(friend):
        raise HTTPException(
            status_code=404,
            detail="Friend not found.",
        )
    return friend
