import uvicorn

from contextlib import contextmanager

from fastapi import FastAPI, Depends

from api.api_v1.api import api_router
from api.deps import get_db
from queue_r.queue_rabmq import queue_rabbit
from services.post import post_srv
from services.dialog import dialog_srv
from services.friend import friend_srv
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
        await friend_srv.cache_top_popular_users(db=db)
        logger.info(f'top popular users cached')
        await friend_srv.cache_top_users_friends(db=db)
        logger.info(f'friends of top popular users cached')
    await queue_rabbit.connect()
    await queue_rabbit.declare_queue("post")    # just to see it dashboard. TODO delete from here
    yield
    
    await queue_rabbit.close()
    logger.info(f'stop App')


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix=get_settings().API_V1_STR)


if __name__ == "__main__":
    logger.info(f'main at port={get_settings().app_port}')
    uvicorn.run("main:app", host="0.0.0.0", port=int(get_settings().app_port), reload=True)
    logger.info('exit main')
