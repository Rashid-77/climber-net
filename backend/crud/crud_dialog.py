from typing import List

from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.user import User
from models.dialog import Dialog
from schemas.dialog import DialogInfoCreate, DialogInfoFull

from utils.log import get_logger
logger = get_logger(__name__)


class CRUDDialog(CRUDBase[Dialog, DialogInfoCreate, DialogInfoFull]):
    def create(self, db: Session, user_a: int, user_b: int) -> Dialog:
        db_obj = Dialog(user_a=min(user_a, user_b), 
                        user_b=max(user_a, user_b))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, user_a: int, user_b: int) -> DialogInfoFull:
        a = min(user_a, user_b)
        b = max(user_a, user_b)
        return db.query(Dialog) \
                    .filter(and_(Dialog.user_a == a, 
                                 Dialog.user_b == b)).first()

    def get_multi(self, 
                  db: Session, 
                  skip: int = 0, 
                  limit: int = 100
                  ) -> List[DialogInfoFull]:
        return super().get_multi(db, skip=skip, limit=limit)
    
    def get_dialog_info(self, db: Session, id: int) -> Dialog:
        ''' Get info on dialog between two users. Users's id, dialog creating date '''
        return db.execute(text("SELECT * FROM dialog WHERE id=:id;"), {'id':id}).first()


dialog = CRUDDialog(Dialog)
