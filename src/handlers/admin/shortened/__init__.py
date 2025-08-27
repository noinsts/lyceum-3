from typing import List

from aiogram import Router

from .hub import HubHandler
from .set import SetHandler


def get_shortened_routers() -> List[Router]:
    """Повертає список роутерів для управління скороченням днів"""
    return [
        HubHandler().get_router(),
        SetHandler().get_router()
    ]
