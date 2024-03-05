from datetime import datetime

from db.tarantool.db import TarantoolSqlDialog
from models.dialog import Dialog
from schemas.dialog import DialogInfoFull


class CRUDDialog:
    def create(self, db: TarantoolSqlDialog, user_a: int, user_b: int) -> Dialog:
        row = self.get_by_users(db, user_a, user_b)
        if row:
            return row
        res = db.insert(min(user_a, user_b), max(user_a, user_b))
        if res is None or not len(res.data):
            return None
        return Dialog(
            id=res.data[0].get("autoincrement_ids")[0], user_a=user_a, user_b=user_b
        )

    def get(self, db: TarantoolSqlDialog, id: int) -> DialogInfoFull:
        row = db.select(id)
        if row is not None:
            return DialogInfoFull(
                id=row[0],
                user_a=row[1],
                user_b=row[2],
                created=datetime.strptime(str(row[3])[:-3], "%Y-%m-%dT%H:%M:%S.%f"),
            )

    def get_by_users(
        self, db: TarantoolSqlDialog, user_a: int, user_b: int
    ) -> DialogInfoFull:
        row = db.select_by_users(min(user_a, user_b), max(user_a, user_b))
        if row is not None and len(row):
            return DialogInfoFull(
                id=row[0],
                user_a=row[1],
                user_b=row[2],
                created=datetime.strptime(str(row[3])[:-3], "%Y-%m-%dT%H:%M:%S.%f"),
            )

    def get_multu(self, db: TarantoolSqlDialog) -> DialogInfoFull:
        dialogs = db.select_all()
        if dialogs is not None and len(dialogs):
            return [
                DialogInfoFull(
                    id=row[0],
                    user_a=row[1],
                    user_b=row[2],
                    created=datetime.strptime(str(row[3])[:-3], "%Y-%m-%dT%H:%M:%S.%f"),
                )
                for row in dialogs
            ]
        return []

    def delete(self, db: TarantoolSqlDialog, id: int):
        d = db.select(id)
        if d is None:
            return None
        res = db.delete(id)
        if res.data[0].get("row_count") == 1:
            return Dialog(
                id=id,
                user_a=d[1],
                user_b=d[2],
                created=datetime.strptime(str(d[3])[:-3], "%Y-%m-%dT%H:%M:%S.%f"),
            )


dialog = CRUDDialog()
