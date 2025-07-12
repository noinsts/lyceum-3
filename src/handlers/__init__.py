from aiogram import Router

from .all import get_a_router
from .student import get_student_router
from .teacher import get_teacher_router
from .admin import get_admin_router
from .common import get_common_router
from .docs_callbacks import get_docs_routers


def get_all_router() -> Router:
    main_router = Router()

    main_router.include_router(get_a_router())

    for router in get_student_router():
        main_router.include_router(router)

    for router in get_teacher_router():
        main_router.include_router(router)

    for router in get_admin_router():
        main_router.include_router(router)

    for router in get_docs_routers():
        main_router.include_router(router)

    main_router.include_router(get_common_router())

    return main_router
