from aiogram import Router

from .all_week import AllWeekHandler
from .my_post import MyPostHandler
from .lessons_by_day import LessonsByDaysHandler
from .academy_time import AcademyTimeHandler
from .olymp import get_olymp_router
from src.middlewares import RoleAccessMiddleware


def get_teacher_router() -> Router:
    """Повертає вчительський роутер з підключеним middleware"""
    router = Router(name='teacher')

    routers = [
        AllWeekHandler().get_router(),
        MyPostHandler().get_router(),
        LessonsByDaysHandler().get_router(),
        AcademyTimeHandler().get_router(),
        *get_olymp_router()
    ]

    for r in routers:
        router.include_router(r)

    router.message.middleware(RoleAccessMiddleware.for_teachers())
    router.callback_query.middleware(RoleAccessMiddleware.for_teachers())

    return router
