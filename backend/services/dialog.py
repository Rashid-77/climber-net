from typing import List

import crud
import schemas
from cache.dialog import dialog_cache
from db.tarantool.db import TarantoolSqlDialog, TarantoolSqlDialogMsg
from models import DialogMessage, User
from utils.log import get_logger

logger = get_logger(__name__)


class DialogService:
    async def save_dialog_msg(
        self,
        db_td: TarantoolSqlDialog,
        db_tdm: TarantoolSqlDialogMsg,
        to_user: User,
        from_user: User,
        msg_in: schemas.DialogMsgCreate,
    ) -> DialogMessage:
        dialog = crud.dialog.create(db_td, user_a=from_user.id, user_b=to_user.id)
        d = crud.dialog_msg.create(
            db_tdm, dialog=dialog, obj_in=msg_in, to_user=to_user, from_user=from_user
        )
        tops = crud.dialog_msg.get_top_dialogs(db_tdm)
        if d.dialog_id in [top.id for top in tops]:
            await dialog_cache.lpush_dialog_msg(d)
        return d

    async def load_dialog_msg_list(
        self,
        db_td: TarantoolSqlDialog,
        db_tdm: TarantoolSqlDialogMsg,
        user_a: User,
        user_b: User,
        limit: int,
        offset: int,
    ) -> List[DialogMessage]:
        dialog = crud.dialog.get_by_users(db_td, user_a=user_a.id, user_b=user_b.id)
        tops = crud.dialog_msg.get_top_dialogs(db_tdm)
        if dialog is None or dialog.id not in [top.id for top in tops]:
            return crud.dialog_msg.get_dialog_list(
                db_tdm, user_a=user_a.id, user_b=user_b.id, limit=limit, offset=offset
            )
        dialog_msgs = await dialog_cache.get_dialog_msgs(
            dialog.id, limit=limit, offset=offset
        )
        if not dialog_msgs:
            dialog_msgs = crud.dialog_msg.get_dialog_list(
                db_tdm, user_a=user_a.id, user_b=user_b.id
            )
            await dialog_cache.cach_list(dialog_msgs)
        return dialog_msgs

    async def warmup_dialogs(self, db_tdm: TarantoolSqlDialogMsg):
        tops = crud.dialog_msg.get_top_dialogs(db_tdm)
        for d in [top for top in tops]:
            cache_len = await dialog_cache.len_dialog_msg(d.id)
            dialog_msgs = crud.dialog_msg.get_dialog_list(
                db_tdm, user_a=d.user_a, user_b=d.user_b
            )
            if cache_len < len(dialog_msgs):
                await dialog_cache.cach_list(dialog_msgs)


dialog_srv = DialogService()
