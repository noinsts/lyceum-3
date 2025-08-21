from typing import List

from aiogram import Router

from .hub import HubHandler


def get_interesting_routers() -> List[Router]:
    """Повертає список роутерів для управління цікавою кнопкою"""
    return [
        HubHandler().get_router()
    ]
