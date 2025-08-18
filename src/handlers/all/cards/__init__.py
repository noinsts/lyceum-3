from typing import List

from aiogram import Router

from .hub import HubHandler

def get_all_cards_routers() -> List[Router]:
    """Повертає список роутерів для управління колекціями карток"""
    return [
        HubHandler().get_router()
    ]
