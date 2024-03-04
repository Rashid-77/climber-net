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

    def clean_dialog_msg_db(self):
        all_msgs = dialog_msg.get_multi(dial_msg_mdb)
        for d in all_msgs:
            dialog_msg.delete(dial_msg_mdb, id=d.id)

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

    def test_get_all_dialog_msg(self, u_id1=1, u_id2=2):
        self.clean_dialog_msg_db()
        all_msgs = dialog_msg.get_multi(dial_msg_mdb)
        assert len(all_msgs) == 0

        dial = dialog.create(dialog_mdb, u_id1, u_id2)
        u1, u2 = User(id=u_id1), User(id=u_id2)
        msgs = ("f1", "f2", "f3", "f4", "f5", "f6")
        for m in msgs:
            dialog_msg.create(
                dial_msg_mdb,
                dialog=dial,
                obj_in=DialogMsgCreate(content=m),
                from_user=u1,
                to_user=u2,
            )
        all_msgs = dialog_msg.get_multi(dial_msg_mdb, skip=3, limit=2)

        assert len(all_msgs) == 2
        assert all_msgs[0].content == "f4"
        assert all_msgs[1].content == "f5"

    def test_get_list_dialog_msg(self, u_id1=1, u_id2=2):
        self.clean_dialog_msg_db()
        all_msgs = dialog_msg.get_multi(dial_msg_mdb)
        assert len(all_msgs) == 0
        data = [
            ("hi", 1, 2),
            ("how r u?", 1, 2),
            ("im ok", 2, 1),
            ("hey alice", 2, 3),
            ("watsup?", 1, 4),
            ("nothing", 4, 1),
            ("is anybody home?", 3, 4),
            ("what r u doing?", 2, 1),
        ]
        dial = dialog.create(dialog_mdb, u_id1, u_id2)
        for d in data:
            dialog_msg.create(
                dial_msg_mdb,
                dialog=dial,
                obj_in=DialogMsgCreate(content=d[0]),
                from_user=User(id=d[1]),
                to_user=User(id=d[2]),
            )
        all_msgs = dialog_msg.get_multi(dial_msg_mdb)
        assert len(all_msgs) == len(data)

        dial = dialog_msg.get_dialog_list(dial_msg_mdb, 1, 4)
        assert dial[0].from_user_id == 1
        assert dial[0].to_user_id == 4
        assert dial[0].content == data[5][0]
        assert dial[1].from_user_id == 1
        assert dial[1].to_user_id == 4
        assert dial[1].content == data[4][0]
