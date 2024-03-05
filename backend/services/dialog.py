from typing import List

import crud
import schemas
from cache.dialog import dialog_cache
from models import DialogMessage, User
from sqlalchemy.orm import Session
from utils.log import get_logger

logger = get_logger(__name__)


class DialogService:
    async def save_dialog_msg(
        self,
        db: Session,
        to_user: User,
        from_user: User,
        msg_in: schemas.DialogMsgCreate,
    ) -> schemas.DialogMsgRead:
        dialog = crud.dialog.get(db, user_a=from_user.id, user_b=to_user.id)
        if not dialog:
            dialog = crud.dialog.create(db, user_a=from_user.id, user_b=to_user.id)
        d = crud.dialog_msg.create(
            db, dialog=dialog, obj_in=msg_in, to_user=to_user, from_user=from_user
        )
        tops = crud.dialog.get_top_dialogs(db)
        if d.dialog_id in [top.id for top in tops]:
            await dialog_cache.lpush_dialog_msg(d)
        return d

    async def load_dialog_msg_list(
        self, db: Session, user_a: User, user_b: User, limit: int, offset: int
    ) -> List[DialogMessage]:
        dialog = crud.dialog.get(db, user_a=user_a.id, user_b=user_b.id)
        tops = crud.dialog.get_top_dialogs(db)
        if dialog.id not in [top.id for top in tops]:
            return crud.dialog_msg.get_dialog_list(
                db, user_a=user_a.id, user_b=user_b.id, limit=limit, offset=offset
            )
        dialog_msgs = await dialog_cache.get_dialog_msgs(
            dialog.id, limit=limit, offset=offset
        )
        if not dialog_msgs:
            dialog_msgs = crud.dialog_msg.get_dialog_list(
                db, user_a=user_a.id, user_b=user_b.id, limit=None, offset=None
            )
            await dialog_cache.cach_list(dialog_msgs)
        return dialog_msgs

    async def warmup_dialogs(self, db: Session):
        tops = crud.dialog.get_top_dialogs(db)
        for d in [top for top in tops]:
            cache_len = await dialog_cache.len_dialog_msg(d.id)
            dialog_msgs = crud.dialog_msg.get_dialog_list(
                db, user_a=d.user_a, user_b=d.user_b, limit=None, offset=None
            )
            if cache_len < len(dialog_msgs):
                await dialog_cache.cach_list(dialog_msgs)


dialog_srv = DialogService()
