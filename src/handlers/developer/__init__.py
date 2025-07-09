from aiogram import Router

from .access import get_access_routers
# from src.middlewares import DeveloperCheckerMiddleware


def get_dev_routers() -> Router:
    """Повертає роутер developer з підключенним middleware"""
    router = Router(name="developer")

    for r in get_access_routers():
        router.include_router(r)

    # router.message.middleware(DeveloperCheckerMiddleware())
    # router.callback_query.middleware(DeveloperCheckerMiddleware())

    return router
