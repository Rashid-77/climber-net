from contextlib import contextmanager

import uvicorn
from aio_pika import ExchangeType
from api.api_v1.api import api_router
from api.deps import get_db
from db.tarantool.db import dial_msg_mdb
from fastapi import FastAPI
from queue_r.queue_rabmq import queue_rabbit
from services.dialog import dialog_srv
from services.friend import friend_srv
from services.post import post_srv
from utils import get_settings
from utils.log import get_logger

logger = get_logger(__name__)


async def lifespan(app: FastAPI):
    logger.info("start App")
    with contextmanager(get_db)() as db:
        await post_srv.warming_up_post_cache(db=db)
        logger.info("posts warmed up")
        await dialog_srv.warmup_dialogs(db_tdm=dial_msg_mdb)
        logger.info("dialogs warmed up")
        await friend_srv.cache_top_popular_users(db=db)
        logger.info("top popular users cached")
        await friend_srv.cache_top_users_friends(db=db)
        logger.info("friends of top popular users cached")
    await queue_rabbit.connect()
    await queue_rabbit.declare_exchange("post_ex", ExchangeType.FANOUT)
    yield

    await queue_rabbit.close()
    logger.info("stop App")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix=get_settings().API_V1_STR)


if __name__ == "__main__":
    logger.info(f"main at port={get_settings().app_port}")
    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(get_settings().app_port), reload=True
    )
    logger.info("exit main")
