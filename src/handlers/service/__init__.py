from aiogram import Router

from .cancel_fsm import CancelFSMHandler
from .teacher_verify import TeacherVerifyHandler


def get_service_router() -> Router:
    """Повертає сервісний роутер"""
    router = Router(name="service")

    routers = [
        CancelFSMHandler().get_router(),
        TeacherVerifyHandler().get_router()
    ]

    for r in routers:
        router.include_router(r)

    return router
