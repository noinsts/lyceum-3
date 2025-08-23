from aiogram import Router

from .calls import CallsHandler
from .today_shortened import TodayShortenedHandler
from .resources import ResourcesHandler
from .cards import get_all_cards_routers


def get_a_router() -> Router:
    """Повертає роутер зі спільними хендлерами вчителів та учнів"""
    router = Router(name="all")

    routers = [
        CallsHandler().get_router(),
        TodayShortenedHandler().get_router(),
        ResourcesHandler().get_router(),
        *get_all_cards_routers()
    ]

    for r in routers:
        router.include_router(r)

    return router
