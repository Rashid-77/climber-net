import datetime as dt
import json
from typing import Optional

from aioredis import Redis
from fastapi.encoders import jsonable_encoder

from cache import fail_silently
from models import Post
from utils.config import get_settings
from utils.converters import map_to
from utils.log import get_logger


logger = get_logger(__name__)

def get_redis(host, port):
    return Redis(host=host, port=port, decode_responses=True)



class PostCache(Redis):
    POSTS_EX: int = int(dt.timedelta(minutes=1).total_seconds())

    def __init__(self, host, port):
        logger.info(f'{host=}, {port=}')
        self._cache = get_redis(host=host, port=port)

    @fail_silently()
    async def get_post(self, post_id: int) -> Optional[Post]:
        cached_post = await self._cache.get(f"posts:{post_id}")
        logger.info(f'{cached_post=}, {type(cached_post)=}')
        return cached_post and map_to(cached_post, Post)

    @fail_silently()
    async def set_post(self, post: Post) -> None:
        await self._cache.set(f"posts:{post.id}",
                              json.dumps(jsonable_encoder(post)),
                              expire=PostCache.POSTS_EX)

    @fail_silently()
    async def unset_post(self, post_id: int) -> None:
        await self._cache.delete(f"posts:{post_id}")


post_cache = PostCache(
                       host=get_settings().redis_host, 
                       port=get_settings().redis_port)
