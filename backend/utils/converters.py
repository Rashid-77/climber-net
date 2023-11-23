import json
from typing import Any, TypeVar, Type, List

# from pydantic import parse_obj_as

T = TypeVar("T")

from utils.log import get_logger
logger = get_logger(__name__)


def map_to(obj: Any, to_type: Type[T]) -> T:
    """
    Convert object to a pydantic BaseModel class.

    :param obj: object to convert
    :param to_type: destination pydantic type
    :return: converted object
    """
    _dict = json.loads(obj)
    return to_type(**_dict)


def strlist_to_list(s: str) -> list:
    if s is None:
        return []
    s = s[1:-1]
    if len(s) == 0:
        return []
    s = s.strip().split(',')
    if len(s) == 0:
        return []
    return [int(i.strip()) for i in s]
