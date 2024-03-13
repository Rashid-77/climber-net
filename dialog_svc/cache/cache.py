import hashlib
import json
from functools import wraps
from typing import Any

from aioredis import Redis
from fastapi.encoders import jsonable_encoder
from utils.config import get_settings
from utils.log import get_logger

logger = get_logger(__name__)


def get_redis(host, port):
    return Redis(host=host, port=port, decode_responses=True)


def fail_silently(default: Any = None):
    """Cache shouldn't make requests fail if cache backend is unavailable
    or not responding.
    When not in production mode, this decorator is ignored to ease debugging."""

    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except Exception as e:
                if not get_settings().prod:
                    raise e
                logger.error("Cache access failed")
                return default

        return wrapper

    return decorator


def hash_cache_key(*args):
    """Generate a key from (hashable) parameters."""
    # cannot use hash(args) since hash function is not stable since Python 3.3
    return hashlib.md5(json.dumps(jsonable_encoder(args)).encode()).hexdigest()
