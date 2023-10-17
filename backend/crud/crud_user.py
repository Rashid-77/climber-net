from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend import get_logger
from backend.crud.base import CRUDBase
from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate
from backend.utils.security import get_password_hash, verify_password

from .base import ModelType

logger = get_logger(__name__)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        if not isinstance(id, int):
            try:
                id = int(id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Incorrect value")
        q = db.execute(text('SELECT * FROM "user" WHERE id=:id;'), {"id": id})
        r = q.fetchone()
        if r is None:
            raise HTTPException(status_code=404, detail="Not found")
        return self.pack_model_user(r)

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            hashed_password=get_password_hash(obj_in.password),
            birthdate=obj_in.birthdate,
            bio=obj_in.bio,
            city=obj_in.city,
            country=obj_in.country,
            disabled=obj_in.disabled,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            # update_data = obj_in.dict(exclude_unset=True) # deprecated
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, username: str, password: str
    ) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return not user.disabled

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    def pack_model_user(self, row) -> User:
        # TODO do it later by sqlalchemy
        return User(
            id=row[0],
            username=row[1].strip(),
            first_name=row[2].strip(),
            last_name=row[3].strip(),
            birthdate=row[4],
            bio=row[5].strip(),
            city=row[6].strip(),
            country=row[7].strip(),
            disabled=row[9],
        )


user = CRUDUser(User)
