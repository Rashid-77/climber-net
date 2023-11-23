from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from api.api_v1.api import api_router
from api.deps import get_db
from services.post import post_srv
from utils import get_settings
from utils.log import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f'start App')
    post_srv.warming_up_post_cache(db = Depends(get_db))
    yield
    logger.info(f'stop App')


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix=get_settings().API_V1_STR)
