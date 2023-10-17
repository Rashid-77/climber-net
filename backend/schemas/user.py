from datetime import date
from typing import Optional

from pydantic import BaseModel


# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: str
    last_name: str
    birthdate: date
    bio: str
    city: str
    country: str
    disabled: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    password: str
    is_superuser: bool = False


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    # class Config:
    #     orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


# class UserId(BaseModel):
#     id: Optional[int] = None


# class UserBase(BaseModel):
#     username: Optional[str] = None
#     first_name: str
#     last_name: str
#     birthdate: date
#     bio: str
#     city: str
#     country: str
#     is_superuser: bool = False


# # Properties to receive via API on creation
# class UserCreate(UserBase):
#     username: str
#     password: str


# # Properties to receive via API on update
# class UserUpdate(UserBase):
#     password: Optional[str] = None


# class UserToDB(UserId, UserCreate):
#     disabled: bool | None = False


# class UserInDB(UserToDB):
#     hashed_password: str


# # Additional properties to return via API
# class User(UserBase, UserId):
#     disabled: bool | None = False
