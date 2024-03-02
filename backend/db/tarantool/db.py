import tarantool
from utils.config import get_settings

t_url = get_settings().tarantool_url
t_port = get_settings().tarantool_port


class TarantoolSqlDialog:
    """message dialog schema beetween 2 users"""

    def __init__(self, url: str = "tarantool", port: int = 3301):
        self.conn = tarantool.connect(url, port)

    def insert(self, u_id_1, u_id_2):
        return self.conn.call("dialog_insert", (u_id_1, u_id_2))

    def select(self, id):
        """Returns None if not found"""
        d = self.conn.call("dialog_select", (id))
        if len(d.data[0].get("rows")):
            return d.data[0].get("rows")[0]

    def select_by_users(self, u_id1, u_id2):
        d = self.conn.call("dialog_select_by_users", (u_id1, u_id2))
        if d.data[0]:
            return d.data[0].get("rows")
        return []

    def select_all(self):
        d = self.conn.call("dialog_select_all")
        if d.data[0]:
            return d.data[0].get("rows")
        return []

    def delete(self, id):
        """
        Returns " - {'row_count': 0}" if not found
        and returns " - {'row_count': 1}" if deleted
        """
        return self.conn.call("dialog_del", (id))


class TarantoolSqlDialogMsg:
    """crud for meaages beetween 2 users"""

    def __init__(self, url: str = "tarantool", port: int = 3301):
        self.conn = tarantool.connect(url, port)

    def insert(self, dial_id, u_id_1, u_id_2, msg):
        return self.conn.call(
            "dialmsg_insert", (dial_id, u_id_1, u_id_2, msg, False, False, False)
        )


dialog_mdb = TarantoolSqlDialog(url=t_url, port=t_port)
dial_msg_mdb = TarantoolSqlDialogMsg(url=t_url, port=t_port)
