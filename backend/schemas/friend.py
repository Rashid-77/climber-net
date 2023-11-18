from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class FriendBase(BaseModel):
    user_a: int
    user_b: int
    status: int
    created: Optional[datetime] = None


# Properties to receive via API on creation
class FriendCreate(FriendBase):
    user_a: int
    user_b: int
    status: int


# Properties to receive via API on update
class FriendUpdate(FriendBase):
    user_a: int
    user_b: int
    status: int


class FriendInDBBase(FriendBase):
    id: Optional[int] = None

    # class Config:
    #     orm_mode = True


# Additional properties to return via API
class Friend(FriendInDBBase):
    pass


class FriendInDB(FriendInDBBase):
    pass
