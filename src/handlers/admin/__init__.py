from aiogram import Router

from .hub import AdminHubHandler
from .forms import get_form_admin_routers
from .schedule import get_admin_schedule_routers
from .shortened import get_shortened_routers
from .broker import AdminBroker

from src.middlewares import RoleAccessMiddleware


def get_admin_router() -> Router:
    """Повернення адмінського роутеру з підключеним middleware"""
    router = Router(name="admin")

    routers = [
        AdminHubHandler().get_router(),
        AdminBroker().get_router(),
        *get_form_admin_routers(),
        *get_admin_schedule_routers(),
        *get_shortened_routers()
    ]

    for r in routers:
        router.include_router(r)

    router.message.middleware(RoleAccessMiddleware.for_admins())
    router.callback_query.middleware(RoleAccessMiddleware.for_admins())

    return router
