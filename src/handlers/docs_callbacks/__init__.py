from typing import List

from aiogram import Router

from .teacher_verify import TeacherVerifyHandler


def get_docs_routers() -> List[Router]:
    """Повертає всі роутери директорії"""
    return [
        TeacherVerifyHandler().get_router()
    ]
