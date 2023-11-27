import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class DialogCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4096)


class DialogRead(DialogCreate):
    from_user_id: int
    to_user_id: int
    created_at: dt.datetime

class DialogUpdate(DialogCreate):
    user_id: int
