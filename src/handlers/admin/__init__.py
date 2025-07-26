from aiogram import Router

from .announcement_hub import AnnouncementHub
from .students_change_schedule import StudentsChangeSchedule
from .teachers_change_schedule import TeachersChangeSchedule
from .meeting import Meeting
from .announcement import get_announcement_router

from src.middlewares import RoleAccessMiddleware


def get_admin_router() -> Router:
    """Повернення адмінського роутеру з підключеним middleware"""
    router = Router(name="admin")

    routers = [
        AnnouncementHub().get_router(),
        StudentsChangeSchedule().get_router(),
        TeachersChangeSchedule().get_router(),
        Meeting().get_router()
        *get_announcement_router(),
    ]

    for r in routers:
        router.include_router(r)

    router.message.middleware(RoleAccessMiddleware.for_admins())
    router.callback_query.middleware(RoleAccessMiddleware.for_admins())

    return router
