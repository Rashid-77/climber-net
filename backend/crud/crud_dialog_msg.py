from typing import List

from crud.base import CRUDBase
from models.dialog import Dialog, DialogMessage
from models.user import User
from schemas.dialog import DialogInfoStat
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

    def get_top_dialogs(self, db: Session) -> List[DialogInfoStat]:
        # TODO check if top_chatters exists in cache
        stmt = """
                SELECT dm.dialog_id, d.user_a, d.user_b, count(*) as cnt
                FROM dialogmessage as dm
                JOIN dialog as d ON d.id = dm.dialog_id
                GROUP BY dialog_id, d.user_a, d.user_b
                ORDER BY cnt DESC
                """
        top_chatters = [
            DialogInfoStat(id=r[0], user_a=r[1], user_b=r[2], cnt_msg=r[3])
            for r in db.execute(text(stmt))
        ]
        # TODO limit top
        top_chatters = top_chatters[:3]
        # TODO put top_chatters to cache
        return top_chatters


dialog_msg = CRUDDialogMsg(DialogMessage)
