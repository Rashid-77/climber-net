from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int] = None
    username: str
    first_name: str
    last_name: str
    age: int
    bio: str
    city: str
    country: str
    password: str
    disabled: bool | None = False
