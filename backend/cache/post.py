import datetime as dt
import json
from typing import List, Optional

from aioredis import Redis
from fastapi.encoders import jsonable_encoder

from cache.cache import get_redis, fail_silently, hash_cache_key
from models import Post
from utils.config import get_settings
from utils.converters import map_to, strlist_to_list
from utils.log import get_logger


logger = get_logger(__name__)


class PostCache(Redis):
    POSTS_EX: int = int(dt.timedelta(minutes=1).total_seconds())
    POSTS_POP_EX: int = int(dt.timedelta(minutes=60).total_seconds())
    POSTS_IDS_EX: int = int(dt.timedelta(minutes=60*24).total_seconds())

    def __init__(self, host, port):
        self._cache = get_redis(host=host, port=port)
    
    # single post section
    @fail_silently()
    async def get_post(self, post_id: int) -> Optional[Post]:
        logger.info('post_cache.get_post()')
        cached_post = await self._cache.get(f"posts:{post_id}")
        logger.info(f'{cached_post=}, {type(cached_post)=}')
        return cached_post and map_to(cached_post, Post)

    @fail_silently()
    async def set_post(self, post: Post, expire: int) -> None:
        await self._cache.set(f"posts:{post.id}",
                              json.dumps(jsonable_encoder(post)),
                              ex=expire)

    @fail_silently()
    async def unset_post(self, post_id: int) -> None:
        await self._cache.delete(f"posts:{post_id}")
    
    # user section
    @fail_silently()
    async def set_posts_ids(self, user_id: int, ids: tuple) -> None:
        await self._cache.set(f"user:{user_id}", 
                              json.dumps(ids), 
                              ex=PostCache.POSTS_IDS_EX)

    @fail_silently()
    async def get_posts_ids(self, user_id: int) -> list:
        ids = await self._cache.get(f"user:{user_id}")
        return strlist_to_list(ids)

    @fail_silently()
    async def unset_posts_ids(self, user_id: int) -> None:
        await self._cache.delete(f"user:{user_id}")

    # milti post section
    @fail_silently()
    async def set_posts(
            self,
            posts: List[Post],
            wall_profile_id: int,
            include_friends: bool,
            older_than: Optional[dt.date]) -> None: 
        
        params_cache_key = hash_cache_key(
            wall_profile_id, include_friends, older_than)
        posts_ids_key = f"walls:{wall_profile_id}:posts:{params_cache_key}"
        pipe = self._cache.pipeline()
        pipe.mset(posts_ids_key, 
                  json.dumps([str(post.id) for post in posts]),
                  *list(sum([(f"posts:{post.id}", json.dumps(jsonable_encoder(post))) 
                             for post in posts], ()))
                )
        for key in [posts_ids_key, *[f"posts:{post.id}" for post in posts]]:
            pipe.expire(key, PostCache.POSTS_EX)
        await pipe.execute()

    @fail_silently()
    async def get_posts(
            self,
            wall_profile_id: int,
            include_friends: bool,
            older_than: dt.datetime) -> Optional[List[Post]]:
        cached_posts_ids = await self._cache.get(
            f"walls:{wall_profile_id}:posts:"
            f"{hash_cache_key(wall_profile_id, include_friends, older_than)}")
        cached_posts_ids = cached_posts_ids and json.loads(cached_posts_ids)
        if not cached_posts_ids:
            return None
        cached_posts = await self._cache.mget(*[f"posts:{post_id}" for post_id in cached_posts_ids])
        return (all(cached_posts) or None) and [map_to(json.loads(post), Post) for post in cached_posts]

    @fail_silently()
    async def unset_posts_ids(
            self,
            wall_profile_id: int,
            include_friends: bool,
            older_than: Optional[dt.date]) -> None:
        await self._cache.delete(
            f"walls:{wall_profile_id}:posts:"
            f"{hash_cache_key(wall_profile_id, include_friends, older_than)}")
        

post_cache = PostCache(host=get_settings().redis_host,
                       port=get_settings().redis_port)
