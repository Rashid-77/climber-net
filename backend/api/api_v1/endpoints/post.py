from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

import models
import crud
import schemas
from api.deps import get_db, get_current_active_user

router = APIRouter()

# from . import get_logger
# logger = get_logger(__name__)


@router.post(
        "/create/", 
        status_code=status.HTTP_201_CREATED, 
        response_model=schemas.post.PostRead)
def create_post(
    post_in: schemas.PostCreate,
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
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
    return crud.post.create(db, obj_in=post_in, current_user=current_user)


@router.post("/feed/", response_model=List[schemas.PostRead])
def feed_posts(
    *,
    offset: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(10, ge=1, le=20),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get friend's posts
    """
    return crud.post.feed_my_friends_post(db, current_user, offset=offset, limit=limit)
