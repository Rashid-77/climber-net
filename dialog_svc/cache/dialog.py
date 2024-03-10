import datetime as dt
import json
from typing import List

from aioredis import Redis
from cache.cache import fail_silently, get_redis
from fastapi.encoders import jsonable_encoder
from models import DialogMessage
from utils.config import get_settings
from utils.converters import map_to
from utils.log import get_logger

logger = get_logger(__name__)


class DialogCache(Redis):
    DIALOG_EX: int = int(dt.timedelta(minutes=1).total_seconds())
    DIALOG_POP_EX: int = int(dt.timedelta(minutes=1).total_seconds())

    def __init__(self, host, port):
        self._cache = get_redis(host=host, port=port)

    @fail_silently()
    async def get_dialog_msgs(
        self, dialog_id: int, limit: int, offset: int
    ) -> List[DialogMessage]:
        """Get slice of list from newest limited"""
        end = offset + limit - 1
        cached = await self._cache.lrange(f"dialog:{dialog_id}", start=offset, end=end)
        return cached and [map_to(c, DialogMessage) for c in cached]

    async def cach_list(self, obj_list: List[DialogMessage]):
        """Push list to cache"""
        for d in obj_list:
            await dialog_cache.rpush_dialog_msg(d)

    @fail_silently()
    async def lpush_dialog_msg(self, dial_msg: DialogMessage) -> None:
        """Push to the list at the top"""
        await self._cache.lpush(
            f"dialog:{dial_msg.dialog_id}", json.dumps(jsonable_encoder(dial_msg))
        )

    @fail_silently()
    async def rpush_dialog_msg(self, dial_msg: DialogMessage) -> None:
        """Push to the list at the end"""
        await self._cache.rpush(
            f"dialog:{dial_msg.dialog_id}", json.dumps(jsonable_encoder(dial_msg))
        )

    @fail_silently()
    async def len_dialog_msg(self, dialog_id: int) -> None:
        return await self._cache.llen(f"dialog:{dialog_id}")

    @fail_silently()
    async def unset_dialog_msg(self, id: int) -> None:
        await self._cache.delete(f"dialog:{id}")


dialog_cache = DialogCache(
    host=get_settings().redis_host, port=get_settings().redis_port
)
