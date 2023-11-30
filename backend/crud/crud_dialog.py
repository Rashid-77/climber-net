from typing import List

from .base import ModelType
from crud.base import CRUDBase
from models.user import User
from models.dialog import Dialog, DialogMessage
from schemas.dialog import DialogMsgCreate, DialogMsgUpdate
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.log import get_logger
logger = get_logger(__name__)

class CRUDDialog(CRUDBase[DialogMessage, DialogMsgCreate, DialogMsgUpdate]):
    def create(self, 
               db: Session,
               dialog: Dialog,
               obj_in: DialogMsgCreate, 
               to_user: User, 
               from_user: User
        ) -> Dialog:
        db_obj = DialogMessage(
            dialog_id = dialog.id,
            from_user_id = from_user.id,
            to_user_id = to_user.id,
            content = obj_in.content,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_dialog_list(self, db: Session, from_user: int, to_user: int) -> List[Dialog]:
        stmt = '''
            select id, content, from_user_id, to_user_id, created_at from dialog
            where (from_user_id=2 and to_user_id=3)
            UNION
            select id, content, from_user_id, to_user_id, created_at from dialog
            where (from_user_id=3 and to_user_id=2)
            order by created_at desc;
            '''
        dialog_list = [r for r in db.execute(text(stmt))]
        for d in dialog_list:
            logger.info(d)
        return dialog_list


dialog = CRUDDialog(Dialog)
