from typing import Any, Dict

from fastapi import Request

CURRENT_USER = 'CURRENT_USER'
REQUEST = 'request'
PLAY_TIME = 60


def add_request(request: Request, data_dict: Dict[str, Any]) -> Dict[str, Any]:
    data_dict[REQUEST] = request
    return data_dict
