from db import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func


class DialogMessage(Base):
    id = Column(Integer, primary_key=True)
    dialog_id = Column(Integer, ForeignKey("dialog.id", ondelete="CASCADE"))
    from_user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    to_user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    content = Column(String, nullable=True)
    read = Column(Boolean, default=False)
    del_by_sender = Column(Boolean, default=False)
    del_by_recipient = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        default=None,
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=True, index=True, default=None
    )

    def __init__(self, **kwargs) -> None:
        """ "data" keyword (list type) have to be, when the model is constructed
        from tarantool response (raw items)"""
        data = kwargs.get("data")
        if data:
            self.id = data[0]
            self.dialog_id = data[1]
            self.from_user_id = data[2]
            self.to_user_id = data[3]
            self.content = data[4]
            self.read = data[5]
            self.del_by_sender = data[6]
            self.del_by_recipient = data[7]
            self.created_at = data[8]
        else:
            super().__init__(**kwargs)


class Dialog(Base):
    """Auxulary table. It is designed to reduce the load on the DialogMessage"""

    id = Column(Integer, primary_key=True)
    user_a = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user_b = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    created = Column(DateTime, default=func.now())
