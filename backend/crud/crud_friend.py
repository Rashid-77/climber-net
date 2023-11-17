from datetime import datetime
import select
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException
from sqlalchemy import and_, text
from sqlalchemy.orm import Session

# from backend import get_logger
from crud.base import CRUDBase
from models.friend import Friend
from schemas.friend import FriendCreate, FriendUpdate

from .base import ModelType

# import get_logger
# logger = get_logger(__name__)


class CRUDFriend(CRUDBase[Friend, FriendCreate, FriendUpdate]):
    def create(self, db: Session, *, obj_in: FriendCreate) -> Friend:
        db_obj = Friend(
            user_a=obj_in.user_a,
            user_b=obj_in.user_b,
            status=obj_in.status,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, user_id, friend_id) -> List[Friend]:
        q1 = db.query(self.model)\
            .filter(
                and_(self.model.user_a == user_id, self.model.user_b == friend_id)
            )
        q2 = db.query(self.model) \
            .filter(
                and_(self.model.user_a == friend_id, self.model.user_b == user_id)
            )
        fr_ids = q1.union(q2).all()
        for q in fr_ids:
            db.delete(q)
        db.commit()
        return fr_ids


friend = CRUDFriend(Friend)
