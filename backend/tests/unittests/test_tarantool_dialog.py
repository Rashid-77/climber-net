from crud.crud_dialog_tarantool import dialog
from db.tarantool.db import dialog_mdb


class TestDialog:
    def test_create_dialog(self, u_id1=1, u_id2=2):
        d = dialog.create(dialog_mdb, u_id1, u_id2)
        assert d is not None
        assert d.id > 0

    def test_get_dialog(self):
        dialog.create(dialog_mdb, 1, 2)
        d = dialog.get_multi(dialog_mdb, 1, 2)
        res = dialog.get(dialog_mdb, id=d[0].id)
        assert res.id == d[0].id

    def test_get_multi_dialog(self, u_id1=1, u_id2=2):
        d = dialog.get_multi(dialog_mdb, u_id1, u_id2)
        assert isinstance(d, list)
        assert d[0].user_a == u_id1
        assert d[0].user_b == u_id2

    def test_delete_dialog(self, id=1):
        d = dialog.get_multi(dialog_mdb, user_a=1, user_b=2)
        res = dialog.delete(dialog_mdb, id=d[0].id)
        assert res.id == d[0].id
