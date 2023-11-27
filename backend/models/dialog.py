from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from db import Base


class Dialog(Base):
    id = Column(Integer, primary_key=True)
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
        default=None
        )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=True, 
        index=True, 
        default=None
        )
