from aiogram import Router

from .timetable import TimetableHandler
from .resources import ResourcesHandler
from .cards import get_all_cards_routers


def get_a_router() -> Router:
    """Повертає роутер зі спільними хендлерами вчителів та учнів"""
    router = Router(name="all")

    routers = [
        TimetableHandler().get_router(),
        ResourcesHandler().get_router(),
        *get_all_cards_routers()
    ]

    for r in routers:
        router.include_router(r)

    return router
