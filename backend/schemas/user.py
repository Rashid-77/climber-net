from pydantic import BaseModel
from typing import Optional


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
