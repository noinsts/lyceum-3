from typing import List

from aiogram import Router

from .calls import CallsHandler

def get_all_router() -> List[Router]:
    """Повертає роутери для всіх користувачів"""

    return [
        CallsHandler.get_router()
    ]
