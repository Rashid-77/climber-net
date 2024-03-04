from typing import List

# from .base import ModelType
from crud.base import CRUDBase
from models.dialog import Dialog, DialogMessage
from models.user import User
from schemas.dialog_msg import DialogMsgCreate, DialogMsgUpdate
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from utils.log import get_logger

logger = get_logger(__name__)


class CRUDDialogMsg(CRUDBase[DialogMessage, DialogMsgCreate, DialogMsgUpdate]):
    def create(
        self,
        db: Session,
        dialog: Dialog,
        obj_in: DialogMsgCreate,
        to_user: User,
        from_user: User,
    ) -> DialogMessage:
        db_obj = DialogMessage(
            dialog_id=dialog.id,
            from_user_id=from_user.id,
            to_user_id=to_user.id,
            content=obj_in.content,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_dialog_list(
        self, db: Session, user_a: int, user_b: int, offset: int = 0, limit: int = 100
    ) -> List[DialogMessage]:
        """Get messages between two users"""
        stmt = """
            SELECT * FROM dialogmessage
            WHERE (from_user_id=:a and to_user_id=:b)
            UNION
            SELECT * FROM dialogmessage
            WHERE (from_user_id=:b and to_user_id=:a)
            ORDER BY id DESC
            LIMIT :lim
            OFFSET :offs;
            """
        dialog_list = db.scalars(
            select(DialogMessage)
            .from_statement(text(stmt))
            .params({"a": user_a, "b": user_b, "lim": limit, "offs": offset})
        ).all()
        return dialog_list


dialog_msg = CRUDDialogMsg(DialogMessage)
