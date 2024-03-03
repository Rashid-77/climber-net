from typing import List

from db.tarantool.db import TarantoolSqlDialogMsg
from models.dialog import Dialog, DialogMessage
from models.user import User
from schemas.dialog_msg import DialogMsgCreate


class CRUDDialogMsg:
    def create(
        self,
        db: TarantoolSqlDialogMsg,
        dialog: Dialog,
        obj_in: DialogMsgCreate,
        to_user: User,
        from_user: User,
    ) -> DialogMessage:
        d = db.insert(
            dialog.id,
            min(to_user.id, from_user.id),
            max(to_user.id, from_user.id),
            obj_in.content,
        )
        if d is None or not len(d.data):
            return None
        return DialogMessage(
            id=d.data[0].get("autoincrement_ids")[0],
            dialog_id=dialog.id,
            from_user_id=from_user.id,
            to_user_id=to_user.id,
            content=obj_in.content,
            read=False,
            del_by_sender=False,
            del_by_recipient=False,
        )

    def get(self, db: TarantoolSqlDialogMsg, id: int) -> DialogMessage:
        d = db.select(id)
        return DialogMessage(data=d)

    def get_multi(self, db: TarantoolSqlDialogMsg) -> List[DialogMessage]:
        d = db.select_all()
        return [DialogMessage(data=row) for row in d]

    def delete(self, db: TarantoolSqlDialogMsg, id: int):
        d = db.select(id)
        if d is None:
            return None
        res = db.delete(id)
        if res.data[0].get("row_count") == 1:
            return DialogMessage(data=d)


dialog_msg = CRUDDialogMsg()
