
from db.tarantool.db import TarantoolSqlDialog

class CRUDDialog():
    def create(self, db: TarantoolSqlDialog, user_a: int, user_b: int):
        db.insert(min(user_a, user_b), max(user_a, user_b))
        

    def get(self, db: TarantoolSqlDialog, user_a: int, user_b: int):
        res = db.select_by_users(min(user_a, user_b), max(user_a, user_b))
        return res


dialog = CRUDDialog()