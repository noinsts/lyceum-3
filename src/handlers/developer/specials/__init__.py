from typing import List

from aiogram import Router

from .admin import AdminListHandler


def get_specials_routers() -> List[Router]:
    """Повертає всіх роутери цього пакету"""
    return [
        AdminListHandler().get_router()
    ]
