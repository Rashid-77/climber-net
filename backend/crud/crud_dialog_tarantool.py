from db.tarantool.db import TarantoolSqlDialog
from schemas.dialog import DialogInfoFull


class CRUDDialog:
    def create(self, db: TarantoolSqlDialog, user_a: int, user_b: int):
        return db.insert(min(user_a, user_b), max(user_a, user_b))

    def get(self, db: TarantoolSqlDialog, user_a: int, user_b: int) -> DialogInfoFull:
        res = db.select_by_users(min(user_a, user_b), max(user_a, user_b))
        # res = DialogInfoFull()
        return res

    def delete(self, db: TarantoolSqlDialog, id: int):
        res = db.delete(id)
        return res


dialog = CRUDDialog()
