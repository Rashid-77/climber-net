import json
from typing import Any, TypeVar, Type

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
