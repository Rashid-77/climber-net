from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    birthdate: Optional[date] = Field(None)
    bio: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    country: Optional[str] = Field(None)
    disabled: Optional[bool] = False


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
