import datetime as dt
import json
from typing import List, Optional

from aioredis import Redis

from cache.cache import get_redis, fail_silently
from models import Post
from utils.config import get_settings
from utils.converters import strlist_to_list
from utils.log import get_logger

logger = get_logger(__name__)


class FriendCache(Redis):
    POPULAR_USERS_EX: int = int(dt.timedelta(minutes=10).total_seconds())

    def __init__(self, host, port):
        self._cache = get_redis(host=host, port=port)

    @fail_silently()
    async def get_popular_users(self) -> Optional[Post]:
        ids = await self._cache.get(f"top_pop_users")
        return strlist_to_list(ids)

    @fail_silently()
    async def set_popular_users(self, users: list) -> None:
        logger.info(f'{users=}, {type(users)=}')
        await self._cache.set(f"top_pop_users",
                              json.dumps(users),
                              ex=FriendCache.POPULAR_USERS_EX)

    @fail_silently()
    async def unset_post(self) -> None:
        await self._cache.delete(f"top_pop_users")


friend_cache = FriendCache(host=get_settings().redis_host,
                       port=get_settings().redis_port)
