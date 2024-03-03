from crud.crud_dialog_msg_tarantool import dialog_msg
from crud.crud_dialog_tarantool import dialog
from db.tarantool.db import dial_msg_mdb, dialog_mdb
from models.user import User
from schemas.dialog_msg import DialogMsgCreate


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


class TestDialogMsg:
    last_dial_msg_id = 0

    def test_create_dialog_msg(
        self,
        from_user_id=1,
        to_user_id=2,
        content="hello",
    ):
        dial = dialog.create(dialog_mdb, from_user_id, to_user_id)
        d = dialog_msg.create(
            dial_msg_mdb,
            dialog=dial,
            obj_in=DialogMsgCreate(content=content),
            to_user=User(id=to_user_id),
            from_user=User(id=from_user_id),
        )
        self.last_dial_msg_id = d.id
        assert d.dialog_id == dial.id
        assert d.from_user_id == 1
        assert d.to_user_id == 2

    def test_get_dialog_msg(self, u_id1=1, u_id2=2):
        dial = dialog.get_multi(dialog_mdb, u_id1, u_id2)
        d1 = dialog_msg.create(
            dial_msg_mdb,
            dialog=dial[0],
            obj_in=DialogMsgCreate(content="something"),
            from_user=User(id=u_id1),
            to_user=User(id=u_id2),
        )

        d = dialog_msg.get(dial_msg_mdb, d1.id)
        assert d1.id == d.id
        assert d1.dialog_id == d.dialog_id
        assert d1.from_user_id == d.from_user_id
        assert d1.to_user_id == d.to_user_id
        assert d1.content == d.content
        assert d1.read == d.read

    def test_delete_dialog_msg(self):
        d = dialog_msg.get_multi(dial_msg_mdb)
        res = dialog_msg.delete(dial_msg_mdb, id=d[0].id)
        assert res.id == d[0].id
