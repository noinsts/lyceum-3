from aiogram import Router

from .access import get_access_routers
from .server_stats import ServerStatsHandler
from .broker import DeveloperBrokerHandler
from .hub import DevHubHandler
from .collections import get_all_collections_routers
from .interesting import get_interesting_routers
from src.middlewares import RoleAccessMiddleware


def get_dev_routers() -> Router:
    """Повертає роутер developer з підключенним middleware"""
    router = Router(name="developer")

    routers = [
        ServerStatsHandler().get_router(),
        DeveloperBrokerHandler().get_router(),
        DevHubHandler().get_router(),
        *get_all_collections_routers(),
        *get_access_routers(),
        *get_interesting_routers()
    ]

    for r in routers:
        router.include_router(r)

    router.message.middleware(RoleAccessMiddleware.for_developers())
    router.callback_query.middleware(RoleAccessMiddleware.for_developers())

    return router
