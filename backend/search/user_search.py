from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, select, and_

from backend import get_logger
from backend import schemas
from backend.models.user import User
from backend.crud.base import ModelType

logger = get_logger(__name__)


class SearchUser(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        Object with methods to search users.

        **Parameters**

        * `model`: A SQLAlchemy model class
        """
        self.model = schemas.User


    def by_first_last_names(
        self, 
        db: Session, 
        f_name: str = "", 
        l_name: str = ""
    ):
        query = """ SELECT *
                    FROM "user"
                    WHERE 
                        LOWER(first_name) LIKE :fn
                        AND
                        LOWER(last_name) LIKE :ln
                    ORDER BY id;
                """
        q = db.execute(text(query), {"fn": f"{f_name}%", "ln": f"{l_name}%"})
        return  q.fetchall()


search_user = SearchUser(User)