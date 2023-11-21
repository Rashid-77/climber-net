import json

from typing import Any, List, Optional
from venv import logger

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

import models
import crud
import schemas
from api.deps import get_db, get_current_active_user
from cache.post import post_cache
from services.post import post_srv
from services.friend import friend_srv

router = APIRouter()


@router.post(
        "/create/", 
        status_code=status.HTTP_201_CREATED, 
        response_model=schemas.PostRead)
async def create_post(
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
    return await post_srv.save_post(db, user=current_user, post_in=post_in)


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
    # get post feed from db in one query
    # return crud.post.feed_my_friends_post(db, current_user, offset=offset, limit=limit)
    raise "New feed not implemented yet !!!"
    friends_ids = friend_srv.get_my_friends(db, current_user.id)
    tops = friend_srv.get_top_popular_users(db)
    
    for fr in friends_ids:
        try:
            tops.remove(fr)
            # read from cache

        except ValueError:
            #read from db
            pass



@router.get("/{post_id}", response_model=schemas.PostRead)
async def get_post(
    post_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get post by id
    """
    post = post_srv.load_post(db, post_id)
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
