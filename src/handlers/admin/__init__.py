from aiogram import Router

from .schedule import get_admin_schedule_routers
from .announcement import get_announcement_router

from src.middlewares import RoleAccessMiddleware


def get_admin_router() -> Router:
    """Повернення адмінського роутеру з підключеним middleware"""
    router = Router(name="admin")

    routers = [
        *get_announcement_router(),
        *get_admin_schedule_routers()
    ]

    for r in routers:
        router.include_router(r)

    router.message.middleware(RoleAccessMiddleware.for_admins())
    router.callback_query.middleware(RoleAccessMiddleware.for_admins())

    return router
