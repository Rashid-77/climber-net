from sqlalchemy import Column, DateTime, Integer
from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db import Base


class FriendshipStatus():
    REJECTED = 0
    ACCEPTED = 1
    UNPROCESSED = 2

class Friend(Base):
    id = Column(Integer, primary_key=True)
    user_a = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user_b = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    status = Column(Integer, nullable=False, default=FriendshipStatus.UNPROCESSED)
    created = Column(DateTime, default=func.now())
