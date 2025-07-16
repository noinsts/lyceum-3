from aiogram import Router

from .teacher_verify import TeacherVerifyHandler


def get_docs_routers() -> Router:
    """Повертає роутер з документаційними хендерами"""
    router = Router(name='docs_callbacks')

    routers = [
        TeacherVerifyHandler().get_router()
    ]

    for r in routers:
        router.include_router(r)

    return router
