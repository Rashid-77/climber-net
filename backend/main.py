from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError

from backend.db import db

from .log import get_logger
from .schemas.token import TokenData
from .schemas.user import User
from .utils.security import ACCESS_TOKEN_EXPIRE_MINUTES  # noqa
from .utils.security import create_access_token  # noqa
from .utils.security import decode_access_token  # noqa
from .utils.security import get_password_hash, verify_password  # noqa

logger = get_logger(__name__)
app = FastAPI()


@app.post("/user/register/")
def register(user: User):
    if db.is_user_exist(user.username):
        return {"msg": "User already exist"}

    user.password = get_password_hash(user.password)
    user.disabled = False
    user = db.insert_into_user(user)
    return {"msg": "User created"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def authenticate_user(username: str, password: str):
    user = db.get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/login/")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user/get/{id}", response_model=User)
def get_user():
    pass
