import json

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

import models
import crud
import schemas
from api.deps import get_db, get_current_active_user
from cache.post import post_cache

router = APIRouter()


@router.post(
        "/create/", 
        status_code=status.HTTP_201_CREATED, 
        response_model=schemas.PostRead)
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


@router.get("/{post_id}", response_model=schemas.PostRead)
async def get_post(
    post_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get post by id
    """
    post = await post_cache.get_post(post_id)
    if not post:
        post = crud.post.get(db, post_id)
        if post:
            await post_cache.set_post(post)

    if not post:
            raise HTTPException(
                status_code=404,
                detail="Post not found.",
            )
    if post.wall_user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission.",
        )
    return post


@router.put("/{post_id}", response_model=schemas.PostRead)
def update_post(
    post_id: int,
    post_in: schemas.PostUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update post by id
    """
    post = crud.post.get(db, post_id)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found.",
        )
    if post.wall_user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission.",
        )
    return crud.post.update(db, db_obj=post, obj_in=post_in)


@router.delete("/{post_id}", response_model=schemas.PostRead)
def delete_posts(
    post_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get post by id
    """
    post = crud.post.get(db, post_id)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found.",
        )
    if post.wall_user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission.",
        )
    post = crud.post.remove(db, id=post_id)
    return post
