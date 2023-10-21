from fastapi import FastAPI

from backend.api.api_v1.api import api_router

from .utils import get_settings

app = FastAPI()

app.include_router(api_router, prefix=get_settings().API_V1_STR)
