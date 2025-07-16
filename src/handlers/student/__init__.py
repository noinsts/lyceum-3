from aiogram import Router

from .all_week import AllWeekHandler
from .lessons_by_day import LessonsTodayHandler, LessonsTomorrowHandler
from .next_lesson import NextLessonHandler
# from .olymps import OlympHandler
from src.middlewares import RoleAccessMiddleware


def get_student_router() -> Router:
    """Повернення студентського роутера з підключенним middleware"""
    router = Router(name='student')

    routers = [
        AllWeekHandler().get_router(),
        LessonsTodayHandler().get_router(),
        LessonsTomorrowHandler().get_router(),
        NextLessonHandler().get_router(),
        # OlympHandler().get_router()
    ]

    for r in routers:
        router.include_router(r)

    router.message.middleware(RoleAccessMiddleware.for_students())
    router.callback_query.middleware(RoleAccessMiddleware.for_students())

    return router
