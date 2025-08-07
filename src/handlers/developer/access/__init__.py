from typing import List

from aiogram import Router

from .hub import AccessHubHandler
from .add import AddAccessHandler
from .block import BlockAccessHandler
from .unblock import UnblockAccessHandler
from .analytics import StatsAccessHandler
from .status import StatusAccessHandler


def get_access_routers() -> List[Router]:
    """Повертає всі роутери developer'а"""
    return [
        AccessHubHandler().get_router(),
        AddAccessHandler().get_router(),
        BlockAccessHandler().get_router(),
        UnblockAccessHandler().get_router(),
        StatsAccessHandler().get_router(),
        StatusAccessHandler().get_router()
    ]
