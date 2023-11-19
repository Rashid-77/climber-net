from typing import List
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .base import ModelType
from crud.base import CRUDBase
from models.user import User
from models.post import PostPrivacy
from models.post import Post
from schemas.post import PostCreate, PostCreateRead
from services.friend import friend_srv
from utils.log import get_logger

logger = get_logger(__name__)


class CRUDPost(CRUDBase[Post, PostCreate, PostCreateRead]):
    def create(self, db: Session, *, obj_in: PostCreate, current_user: User) -> Post:
        obj_in.wall_user_id = obj_in.wall_user_id or current_user.id
        db_obj = Post(
            wall_user_id = obj_in.wall_user_id,
            content = obj_in.content,
            user_id = current_user.id,
            privacy = obj_in.privacy,
            username = current_user.username
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def feed_my_friends_post(
            self, 
            db: Session, 
            user: User, 
            offset: int = 0, 
            limit: int = 10
        ) -> List[ModelType]:
        friends = friend_srv.get_my_friends(db, user.id)
        offset = offset if offset >= 0 else 0
        limit = limit if limit >= 0 else 0
        return db.query(Post) \
                .filter(Post.wall_user_id.in_(friends)) \
                .group_by(Post.id, Post.created_at) \
                .order_by(desc(Post.created_at)) \
                .limit(limit) \
                .offset(offset) \
                .all()


post = CRUDPost(Post)
