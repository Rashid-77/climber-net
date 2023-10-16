from datetime import date
from typing import Optional

from pydantic import BaseModel


class UserId(BaseModel):
    id: Optional[int] = None


class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: str
    last_name: str
    birthdate: date
    bio: str
    city: str
    country: str


class UserCreate(UserBase):
    username: str
    password: str


class UserToDB(UserId, UserCreate):
    disabled: bool | None = False


class UserInDB(UserToDB):
    pass


# Additional properties to return via API
class User(UserBase, UserId):
    disabled: bool | None = False
