from aiogram import Router

from .service import get_service_router
from .all import get_a_router
from .student import get_student_router
from .teacher import get_teacher_router
from .admin import get_admin_router
from .common import get_common_router
from .developer import get_dev_routers


def get_all_router() -> Router:
    main_router = Router()

    main_router.include_router(get_service_router())

    main_router.include_router(get_a_router())

    main_router.include_router(get_student_router())

    main_router.include_router(get_teacher_router())

    main_router.include_router(get_admin_router())

    main_router.include_router(get_dev_routers())

    main_router.include_router(get_common_router())

    return main_router
