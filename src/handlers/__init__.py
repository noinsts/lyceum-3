from aiogram import Router

from .student import get_student_router
from .teacher import get_teacher_router
from .admin import get_admin_router
from .register import RegisterHandler
from .common import CommonHandler


def get_all_router() -> Router:
    main_router = Router()

    for router in get_student_router():
        main_router.include_router(router)

    for router in get_teacher_router():
        main_router.include_router(router)

    for router in get_admin_router():
        main_router.include_router(router)

    main_router.include_router(RegisterHandler().get_router())
    main_router.include_router(CommonHandler().get_router())

    return main_router
