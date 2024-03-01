from crud.crud_dialog_tarantool import dialog
from db.tarantool.db import dialog_mdb


class TestDialog:
    def test_create_dialog(self, u_id1=1, u_id2=2):
        print("")
        d = dialog.create(dialog_mdb, u_id1, u_id2)
        assert d.data[0].get("row_count") == 1

    def test_get(self, u_id1=1, u_id2=2):
        # print()
        d = dialog.get(dialog_mdb, u_id1, u_id2)
        # for row in d:
        #     print(row)
        assert d[0][1] == 1
        assert d[0][2] == 2

    def test_delete(self, id=1):
        # print()
        d = dialog.get(dialog_mdb, 1, 2)
        # print(d[0][0])
        d = dialog.delete(dialog_mdb, id=d[0][0])
        # print(d)
        assert d.data[0].get("row_count") == 1
