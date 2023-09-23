import os

from fastapi import FastAPI

from backend.db import db
from .log import get_logger
from .schemas.user import User
from .utils.security import get_password_hash


logger = get_logger(__name__)
app = FastAPI()


@app.post("/user/register/")
def register(user: User):
    if db.is_user_exist(user.username):
        return {"msg": "User already exist"}

    user.password = get_password_hash(user.password)
    user = db.insert_into_user(user)
    return {"msg": "User created"}


@app.post("/login/")
def login():
    pass


@app.get("/user/get/{id}", response_model=User)
def get_user():
    pass
