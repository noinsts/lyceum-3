from typing import List

from aiogram import Router

from .hub import HubHandler
from .inventory import InventoryHandler

def get_all_cards_routers() -> List[Router]:
    """Повертає список роутерів для управління колекціями карток"""
    return [
        HubHandler().get_router(),
        InventoryHandler().get_router()
    ]
