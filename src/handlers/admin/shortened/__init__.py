from typing import List

from aiogram import Router

from .hub import HubHandler
from .set import SetHandler
from .get import GetHandler


def get_shortened_routers() -> List[Router]:
    """Повертає список роутерів для управління скороченням днів"""
    return [
        HubHandler().get_router(),
        SetHandler().get_router(),
        GetHandler().get_router()
    ]
