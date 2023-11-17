from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import models
from backend import crud, get_logger, schemas
from backend.api import deps
from backend.schemas.friend import FriendCreate
from backend.models.friend import FriendshipStatus
router = APIRouter()

logger = get_logger(__name__)


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
    
    friend = crud.friend.create(
        db, 
        obj_in=FriendCreate(
            user_a=current_user.id, 
            user_b=user_id, 
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
