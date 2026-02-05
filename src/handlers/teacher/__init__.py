from aiogram import Router

from .my_post import MyPostHandler
from .academy_time import AcademyTimeHandler
from .olymp import get_olymp_router
from .form import get_form_routers
from src.middlewares import RoleAccessMiddleware
from .schedule import ScheduleHandler


def get_teacher_router() -> Router:
    """Повертає вчительський роутер з підключеним middleware"""
    router = Router(name='teacher')

    routers = [
        MyPostHandler().get_router(),
        ScheduleHandler().get_router(),
        AcademyTimeHandler().get_router(),
        *get_olymp_router(),
        *get_form_routers()
    ]

    for r in routers:
        router.include_router(r)

    router.message.middleware(RoleAccessMiddleware.for_teachers())
    router.callback_query.middleware(RoleAccessMiddleware.for_teachers())

    return router
