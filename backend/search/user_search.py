from typing import Generic, Type

from sqlalchemy import text
from sqlalchemy.orm import Session

import schemas
from crud.base import ModelType
from models.user import User

# import get_logger
# logger = get_logger(__name__)


class SearchUser(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        Object with methods to search users.

        **Parameters**

        * `model`: A SQLAlchemy model class
        """
        self.model = schemas.User

    def by_first_last_names(self, db: Session, f_name: str = "", l_name: str = ""):
        query = """ SELECT *
                    FROM "user"
                    WHERE
                        first_name LIKE :fn
                        AND
                        last_name LIKE :ln
                    ORDER BY id;
                """
        q = db.execute(
            text(query), {"fn": f"{f_name.lower()}%", "ln": f"{l_name.lower()}%"}
        )
        return q.fetchall()


search_user = SearchUser(User)
