import uvicorn
from api.api_v2.api import api_router as api_router_v2
from db.tarantool.db import t_session
from fastapi import FastAPI
from services.dialog import dialog_srv
from utils import get_settings
from utils.log import get_logger

logger = get_logger(__name__)


async def lifespan(app: FastAPI):
    logger.info("start App")
    await dialog_srv.warmup_dialogs(db=t_session)
    logger.info("dialogs warmed up")
    yield

    logger.info("stop App")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router_v2, prefix=get_settings().API_V2_STR)


if __name__ == "__main__":
    logger.info(f"main at port={get_settings().app_port}")
    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(get_settings().app_port), reload=True
    )
    logger.info("exit main")
