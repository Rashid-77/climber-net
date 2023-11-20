from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

# import enum enum.Enum
class PostPrivacy():
    PUBLIC = 0
    FRIEND = 1

class Post(Base):
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=True)
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
    wall_user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    username = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    privacy = Column(Integer, nullable=False, default=PostPrivacy.PUBLIC)
    comments_count = Column(Integer, server_default="0", nullable=False)
