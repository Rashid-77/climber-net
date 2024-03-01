import tarantool


class TarantoolSqlDialog:
    """ message dialog schema beetween 2 users """

    def __init__(self, url: str = "tarantool", port: int = 3301):
        self.conn = tarantool.connect(url, port)

    def insert(self, u_id_1, u_id_2):
        return self.conn.call("dialog_insert", (u_id_1, u_id_2))

    def select(self, id):
        d = self.conn.call("dialog_select", (id))
        if d.data[0]:
            return d.data[0].get("rows")[0]
        return []

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
        d = self.conn.call("dialog_del", (id))
        return d


dialog_mdb = TarantoolSqlDialog()