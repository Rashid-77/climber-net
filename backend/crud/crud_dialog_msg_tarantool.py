from typing import List

from db.tarantool.db import TarantoolSqlDialogMsg
from models.dialog import Dialog, DialogMessage
from models.user import User
from schemas.dialog import DialogInfoStat
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
        d = db.select(id=d.data[0].get("autoincrement_ids")[0])
        return DialogMessage(data=d)

    def get(self, db: TarantoolSqlDialogMsg, id: int) -> DialogMessage:
        d = db.select(id)
        return DialogMessage(data=d)

    def get_multi(
        self, db: TarantoolSqlDialogMsg, skip: int = 0, limit: int = 100
    ) -> List[DialogMessage]:
        d = db.select_all(skip, limit)
        return [DialogMessage(data=row) for row in d]

    def delete(self, db: TarantoolSqlDialogMsg, id: int):
        d = db.select(id)
        if d is None:
            return None
        res = db.delete(id)
        if res.data[0].get("row_count") == 1:
            return DialogMessage(data=d)

    def get_dialog_list(
        self,
        db: TarantoolSqlDialogMsg,
        user_a: int,
        user_b: int,
        offset: int = 0,
        limit: int = 100,
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
        d = db.get_dialog_(stmt, user_a, user_b, offset, limit)
        return [DialogMessage(data=row) for row in d]

    def get_top_dialogs(self, db: TarantoolSqlDialogMsg) -> List[DialogInfoStat]:
        # TODO check if top_chatters exists in cache
        stmt = """
                SELECT dm.dialog_id, d.user1_id, d.user2_id, count(*) as cnt
                FROM dialogmessage as dm
                JOIN dialog as d ON d.id = dm.dialog_id
                GROUP BY dialog_id, d.user1_id, d.user2_id
                ORDER BY cnt DESC;
                """

        items = db.get_top_dialogs(stmt)
        top_chatters = [
            DialogInfoStat(id=r[0], user_a=r[1], user_b=r[2], cnt_msg=r[3])
            for r in items
        ]
        # TODO limit top
        top_chatters = top_chatters[:3]
        # TODO put top_chatters to cache
        return top_chatters


dialog_msg = CRUDDialogMsg()
