from typing import List

from aiogram import Router

from .hub import HubHandler


def get_all_collections_routers() -> List[Router]:
    """Повертає всі роутери для роботи з колекціями"""
    return [
        HubHandler().get_router()
    ]
