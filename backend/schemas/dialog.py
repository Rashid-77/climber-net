import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class DialogMsgCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4096)


class DialogMsgRead(DialogMsgCreate):
    id: int
    dialog_id: int
    from_user_id: int
    to_user_id: int
    created_at: dt.datetime

class DialogMsgUpdate(DialogMsgCreate):
    user_id: int


class DialogInfoBase(BaseModel):
    id: int
    user_a: int
    user_b: int

class DialogInfoStat(DialogInfoBase):
    cnt_msg: int

class DialogInfoFull(DialogInfoStat):
    created: dt.datetime
