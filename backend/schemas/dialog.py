import datetime as dt

from pydantic import BaseModel


# Shared properties
class DialogInfoCreate(BaseModel):
    user_a: int
    user_b: int


class DialogInfoBase(DialogInfoCreate):
    id: int


class DialogInfoFull(DialogInfoBase):
    created: dt.datetime


class DialogInfoStat(DialogInfoFull):
    cnt_msg: int
