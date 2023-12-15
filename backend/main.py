import uvicorn

from contextlib import contextmanager

from fastapi import FastAPI, Depends

from api.api_v1.api import api_router
from api.deps import get_db
from services.post import post_srv
from services.dialog import dialog_srv
from utils import get_settings
from utils.log import get_logger

logger = get_logger(__name__)


async def lifespan(app: FastAPI):
    logger.info(f'start App')
    with contextmanager(get_db)() as db:
        await post_srv.warming_up_post_cache(db=db)
        logger.info(f'posts warmed up')
        await dialog_srv.warmup_dialogs(db=db)
        logger.info(f'dialogs warmed up')
        
    yield
    logger.info(f'stop App')


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix=get_settings().API_V1_STR)


if __name__ == "__main__":
    logger.info(f'main at port={get_settings().app_port}')
    uvicorn.run(app, host="0.0.0.0", port=int(get_settings().app_port))
    logger.info('exit main')