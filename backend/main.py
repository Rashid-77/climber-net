from fastapi import FastAPI

from backend.api.api_v1.api import api_router

from .log import get_logger
from .utils import get_settings

logger = get_logger(__name__)
app = FastAPI()

app.include_router(api_router, prefix=get_settings().API_V1_STR)


# @app.post("/user/register/", response_model=User)
# def register(user: UserCreate):
#     if db.is_user_exist(user.username):
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this username already exists.",
#         )
#     user.password = get_password_hash(user.password)
#     user = db.insert_into_user(UserToDB(**user.model_dump()))
#     return user


# @app.post("/login/", response_model=Token)
# def login_for_access_token(
#         form_data: Annotated[OAuth2PasswordRequestForm,
#         Depends()]
#     ):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     if user.disabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Inactive user",
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": str(user.id)}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


# @app.get("/user/get/{id}", response_model=User)
# def get_user(id: int, ses: Session = Depends(deps.get_db)):
#     user = db.get_user_by_id(id=id, db=ses)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
#     return user


# @app.get("/user/search", response_model=List[User])
# async def read_item(first_name: str = "", last_name: str = ""):
#     users = db.search_user(first_name, last_name)
#     return users
