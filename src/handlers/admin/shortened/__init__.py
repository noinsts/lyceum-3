from typing import List

from aiogram import Router

from .hub import HubHandler


def get_shortened_routers() -> List[Router]:
    """Повертає список роутерів для управління скороченням днів"""
    return [
        HubHandler().get_router()
    ]
