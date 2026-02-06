from aiogram import Router

from .interesting_button import InterestingButtonHandler
from .olymps import OlympHandler
from .schedule import ScheduleHandler
from src.middlewares import RoleAccessMiddleware


def get_student_router() -> Router:
    """Повернення студентського роутера з підключенним middleware"""
    router = Router(name='student')

    routers = [
        ScheduleHandler().get_router(),
        InterestingButtonHandler().get_router(),
        OlympHandler().get_router()
    ]

    for r in routers:
        router.include_router(r)

    router.message.middleware(RoleAccessMiddleware.for_students())
    router.callback_query.middleware(RoleAccessMiddleware.for_students())

    return router
