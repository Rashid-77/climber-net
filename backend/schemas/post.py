import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field
from models.post import PostPrivacy


# Shared properties
class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4096)
    wall_user_id: Optional[int]
    privacy: int# = PostPrivacy.PUBLIC


class PostCreateRead(BaseModel):
    id: int
    content: str
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]
    wall_user_id: int
    user_id: int
    privacy: int# = PostPrivacy.PUBLIC
    comments_count: int = 0


class PostRead(PostCreateRead):
    username: str
