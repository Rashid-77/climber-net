from typing import List

from crud.base import CRUDBase
from models.dialog import Dialog
from schemas.dialog import DialogInfoCreate, DialogInfoFull, DialogInfoStat
from sqlalchemy import and_, text
from sqlalchemy.orm import Session
from utils.log import get_logger

logger = get_logger(__name__)


class CRUDDialog(CRUDBase[Dialog, DialogInfoCreate, DialogInfoFull]):
    def create(self, db: Session, user_a: int, user_b: int) -> Dialog:
        db_obj = Dialog(user_a=min(user_a, user_b), user_b=max(user_a, user_b))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, user_a: int, user_b: int) -> DialogInfoFull:
        a = min(user_a, user_b)
        b = max(user_a, user_b)
        return (
            db.query(Dialog)
            .filter(and_(Dialog.user_a == a, Dialog.user_b == b))
            .first()
        )

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[DialogInfoFull]:
        return super().get_multi(db, skip=skip, limit=limit)

    def get_dialog_info(self, db: Session, id: int) -> Dialog:
        """Get info on dialog between two users. Users's id, dialog creating date"""
        return db.execute(
            text("SELECT * FROM dialog WHERE id=:id;"), {"id": id}
        ).first()

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


dialog = CRUDDialog(Dialog)
