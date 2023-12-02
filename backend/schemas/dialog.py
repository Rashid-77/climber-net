import datetime as dt

from pydantic import BaseModel, Field


# Shared properties
class DialogInfoCreate(BaseModel):
    user_a: int
    user_b: int

class DialogInfoBase(DialogInfoCreate):
    id: int

class DialogInfoStat(DialogInfoBase):
    cnt_msg: int

class DialogInfoFull(DialogInfoStat):
    created: dt.datetime
