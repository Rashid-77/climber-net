import tarantool
from tarantool import Connection
from utils import get_settings


class TarantoolConn(Connection):
    def __init__(self, url: str = "tarantool", port: int = 3301):
        self.conn = tarantool.connect(url, port)

    def close(self):
        self.conn.close()


t_url = get_settings().tarantool_url
t_port = get_settings().tarantool_port
t_session = TarantoolConn(t_url, t_port).conn


class TarantoolSqlDialog:
    """message dialog schema beetween 2 users"""

    def insert(self, db: TarantoolConn, u_id_1, u_id_2):
        return db.call("dialog_insert", (u_id_1, u_id_2))

    def select(self, db: TarantoolConn, id):
        """Returns None if not found"""
        d = db.call("dialog_select", (id))
        if len(d.data[0].get("rows")):
            return d.data[0].get("rows")[0]

    def select_by_users(self, db: TarantoolConn, u_id1, u_id2):
        d = db.call("dialog_select_by_users", (u_id1, u_id2))
        if d.data[0] and len(d.data[0].get("rows")):
            return d.data[0].get("rows")[0]
        return []

    def select_all(self, db):
        d = db.call("dialog_select_all")
        if d.data[0]:
            return d.data[0].get("rows")
        return []

    def delete_(self, db: TarantoolConn, id):
        """
        Returns " - {'row_count': 0}" if not found
        and returns " - {'row_count': 1}" if deleted
        """
        return db.call("dialog_del", (id))


class TarantoolSqlDialogMsg:
    """crud for messages beetween 2 users"""

    def insert(self, db: TarantoolConn, dial_id, u_id_1, u_id_2, msg: str):
        """
        Returns " - {'autoincrement_ids': [1], 'row_count': 1}" if inserted
        where [1] is a id number
        """
        return db.call(
            "dialmsg_insert", (dial_id, u_id_1, u_id_2, msg, False, False, False)
        )

    def select(self, db: TarantoolConn, id):
        """Returns None if not found"""
        d = db.call("dialmsg_select", (id))
        if len(d.data[0].get("rows")):
            return d.data[0].get("rows")[0]

    def select_all(self, db: TarantoolConn, skip: int = 0, limit: int = 100):
        d = db.call("dialmsg_select_all", (skip, limit))
        if d.data[0]:
            return d.data[0].get("rows")
        return []

    def delete_(self, db: TarantoolConn, id):
        """
        Returns " - {'row_count': 0}" if not found
        returns " - {'row_count': 1}" if deleted
        """
        return db.call("dialogmsg_del", (id))

    def select_dialog(
        self,
        db: TarantoolConn,
        stmt: str,
        u1: int,
        u2: int,
        skip: int = 0,
        limit: int = 100,
    ):
        d = db.execute(stmt, {"a": u1, "b": u2, "offs": skip, "lim": limit})
        return d if len(d) else []

    def select_top_dialogs(self, db: TarantoolConn, stmt: str):
        d = db.execute(stmt)
        return d if len(d) else []
