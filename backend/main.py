from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError

from backend.db import db

from .log import get_logger
from .schemas.token import Token, TokenData
from .schemas.user import User, UserCreate, UserToDB
from .utils.security import ACCESS_TOKEN_EXPIRE_MINUTES  # noqa
from .utils.security import create_access_token  # noqa
from .utils.security import decode_access_token  # noqa
from .utils.security import get_password_hash, verify_password  # noqa

logger = get_logger(__name__)
app = FastAPI()


@app.post("/user/register/", response_model=User)
def register(user: UserCreate):
    if db.is_user_exist(user.username):
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists.",
        )
    user.password = get_password_hash(user.password)
    user = db.insert_into_user(UserToDB(**user.dict()))
    return user


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
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = db.get_user_by_id(id=token_data.user_id)
    logger.info(f"...{user=}")
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


@app.post("/login/", response_model=Token)
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
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user/get/{id}", response_model=User)
def get_user(id: int):
    user = db.get_user_by_id(id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )
    return user


@app.get("/user/search")
async def read_item(first_name: str = "", last_name: str = ""):
    users = db.search_user(first_name, last_name)
    return users
