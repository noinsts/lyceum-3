from aiogram import Router

from .calls import CallsHandler
from .today_shorted import TodayShortedHandler


def get_a_router() -> Router:
    """Повертає роутер зі спільними хендлерами вчителів та учнів"""
    router = Router(name="all")

    routers = [
        CallsHandler().get_router(),
        TodayShortedHandler().get_router()
    ]

    for r in routers:
        router.include_router(r)

    return router
