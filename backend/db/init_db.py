import os

import schemas  # noqa: F401
from sqlalchemy.orm import Session

from backend import crud
# from backend.utils.config import get_settings
from . import base  # noqa: F401

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # from db.base_class import Base
    # from db.session import engine

    # Base.metadata.create_all(bind=engine)

    username = os.getenv("FIRST_SUPERUSER", "")
    passw = os.getenv("FIRST_SUPERUSER_PASSWORD", "")
    user_ = crud.user.get_by_username(db, username=username)
    if not user_:
        user_in = schemas.UserCreate(
            username=username,
            password=passw,
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)  # noqa: F841
