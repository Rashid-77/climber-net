from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: str
    last_name: str
    age: int
    bio: str
    city: str
    country: str


class UserCreate(UserBase):
    username: str
    password: str


class UserToDB(UserCreate):
    id: Optional[int] = None
    disabled: bool | None = False


class UserInDBBase(UserBase):
    id: Optional[int] = None


class UserInDB(UserToDB):
    pass


# Additional properties to return via API
class User(UserBase):
    id: Optional[int] = None
    disabled: bool | None = False
