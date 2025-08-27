from typing import List

from aiogram import Router

from .hub import HubHandler
from .info import InfoHandler
from .broadcast import BroadcastHandler


def get_form_routers() -> List[Router]:
    """Повертає всі вчительські роутери управління класами"""
    return [
        HubHandler().get_router(),
        InfoHandler().get_router(),
        BroadcastHandler().get_router()
    ]
