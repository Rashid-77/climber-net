import datetime as dt
import json
from typing import List, Optional

from aioredis import Redis
from fastapi.encoders import jsonable_encoder

from cache.cache import get_redis, fail_silently, hash_cache_key
from models import Dialog
from utils.config import get_settings
from utils.converters import map_to, strlist_to_list
from utils.log import get_logger


logger = get_logger(__name__)


class DialogCache(Redis):
    DIALOG_EX: int = int(dt.timedelta(minutes=1).total_seconds())
    DIALOG_POP_EX: int = int(dt.timedelta(minutes=1).total_seconds())

    def __init__(self, host, port):
        self._cache = get_redis(host=host, port=port)
    
    # single post section
    @fail_silently()
    async def get_dialog(self, id: int) -> Optional[Dialog]:
        cached = await self._cache.get(f"dialog:{id}")
        return cached and map_to(cached, Dialog)

    @fail_silently()
    async def set_dialog(self, dialog: Dialog, expire: int) -> None:
        await self._cache.set(f"dialog:{dialog.id}",
                              json.dumps(jsonable_encoder(dialog)),
                              ex=expire)

    @fail_silently()
    async def unset_dialog(self, id: int) -> None:
        await self._cache.delete(f"dialog:{id}")
    

dialog_cache = DialogCache(host=get_settings().redis_host, 
                           port=get_settings().redis_port)