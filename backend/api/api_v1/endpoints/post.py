from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

import models
import crud
import schemas
from api.deps import get_db, get_current_active_user
from services.post import post_srv
from utils.log import get_logger
logger = get_logger(__name__)

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
    post = await post_srv.save_post(db, user=current_user, post_in=post_in)
    await post_srv.add_post_created_event(current_user, post_in)
    return post


@router.post("/feed/", response_model=List[schemas.PostRead])
async def feed_posts(
    offset: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(10, ge=1, le=20),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get friend's posts
    """
    logger.info('--------------------')
    logger.info("feed_posts()")
    # get post feed from db in one query
    # return crud.post.feed_my_friends_post(db, current_user, offset=offset, limit=limit)
    posts = await post_srv.feed_friends_posts(db, current_user)
    return posts[offset:offset+limit]


@router.get("/{post_id}", response_model=schemas.PostRead)
async def get_post(
    post_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get post by id
    """
    post = await post_srv.load_post(db, post_id)
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


@router.get("/post/feed/posted", response_class=HTMLResponse)
async def get(request: Request):
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <h2>Your ID: <span id="ws-id"></span></h2>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'>
            </ul>
            <script>
                var client_id = Date.now()
                document.querySelector("#ws-id").textContent = client_id;
                var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    ws.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(html)
