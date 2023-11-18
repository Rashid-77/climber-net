from sqlalchemy import and_
from sqlalchemy.orm import Session

# from backend import get_logger
from crud.base import CRUDBase
from models.post import Post
from schemas.post import PostCreate, PostCreateRead

from .base import ModelType

# import get_logger
# logger = get_logger(__name__)


class CRUDPost(CRUDBase[Post, PostCreate, PostCreateRead]):
    def create(self, db: Session, *, obj_in: PostCreate, current_user_id) -> Post:
        obj_in.wall_user_id = obj_in.wall_user_id or current_user_id
        db_obj = Post(
            wall_user_id = obj_in.wall_user_id,
            content = obj_in.content,
            user_id = current_user_id,
            privacy = obj_in.privacy
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


post = CRUDPost(Post)
