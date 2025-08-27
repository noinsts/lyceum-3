from typing import List

from aiogram import Router

from .add import AddHandler
from .hub import HubHandler


def get_interesting_routers() -> List[Router]:
    """Повертає список роутерів для управління цікавою кнопкою"""
    return [
        AddHandler().get_router(),
        HubHandler().get_router()
    ]
