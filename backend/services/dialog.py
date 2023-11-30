from typing import List

from sqlalchemy import text, and_
from sqlalchemy.sql import exists 
from sqlalchemy.orm import Session

import crud
import schemas

from cache.post import post_cache, PostCache
from models import Dialog, User
from services.friend import friend_srv
from utils.log import get_logger


logger = get_logger(__name__)


class DialogService:

    async def save_dialog(self, 
                          db: Session, 
                          to_user: User, 
                          from_user: User, 
                          msg_in: schemas.DialogMsgCreate
                          ) -> Dialog:
        a = min(to_user.id, from_user.id)
        b = max(to_user.id, from_user.id)
        dialog = self._get_dialog(db, user_a=a, user_b=b)
        
        logger.info(f'{dialog.id=}')
        
        res = crud.dialog.create(db, 
                                 dialog=dialog, 
                                 obj_in=msg_in, 
                                 to_user=to_user, 
                                 from_user=from_user)
        return res
        
    def _get_dialog(self, db: Session, user_a, user_b) -> Dialog:
        res = db.query(Dialog) \
            .filter(and_(Dialog.user_a == user_a, Dialog.user_b == user_b)).first()
        if res:
            logger.info(f'{res.id=}')
            return res
        db_obj = Dialog(user_a=user_a, user_b=user_b)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj) 
        return db_obj                   

    def get_top_dialogs(self, db: Session) -> List[Dialog]:
        stmt = '''
                SELECT dm.dialog_id, d.user_a, d.user_b, count(*) as cnt 
                FROM dialogmessage as dm
                JOIN dialog as d ON d.id = dm.dialog_id
                GROUP BY dialog_id, d.user_a, d.user_b
                ORDER BY cnt DESC
                '''
        top_chatters = [r[0] for r in db.execute(text(stmt)) if r[1] > 0]
        logger.info(f'{top_chatters=}')
        # TODO limit top
        # set to cache top_chatters
        return top_chatters


dialog_srv = DialogService()