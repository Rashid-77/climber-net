from datetime import datetime
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend import get_logger
from backend.crud.base import CRUDBase
from backend.models.friend import Friend
from backend.schemas.friend import FriendCreate, FriendUpdate

from .base import ModelType

logger = get_logger(__name__)


class CRUDFriend(CRUDBase[Friend, FriendCreate, FriendUpdate]):
    def create(self, db: Session, *, obj_in: FriendCreate) -> Friend:
        db_obj = Friend(
            user_a=obj_in.user_a,
            user_b=obj_in.user_b,
            status=obj_in.status,
            created=datetime.now()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


friend = CRUDFriend(Friend)
