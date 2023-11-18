from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import crud
import schemas
from api import deps
# from models.post import PostPrivacy
router = APIRouter()

# from . import get_logger
# logger = get_logger(__name__)


@router.post(
        "/create/", 
        status_code=status.HTTP_201_CREATED, 
        response_model=schemas.post.PostCreate)
def create_post(
    post_in: schemas.PostCreate,
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new post.
      post can be created by author of wall
      post can be commented by post author and author's friend
    """
    if post_in.wall_user_id != current_user.id:
        user = crud.user.get(db, id=post_in.wall_user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )
    return crud.post.create(db, obj_in=post_in, current_user_id=current_user.id)
