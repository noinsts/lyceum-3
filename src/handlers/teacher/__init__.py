from typing import List

from aiogram import Router

from .all_week import AllWeekHandler
from .my_post import MyPostHandler
from .lessons_by_day import LessonsTodayHandler, LessonsTomorrowHandler
from .academy_time import AcademyTime
from .olymp import get_olymp_router


def get_teacher_router() -> List[Router]:
    """Повертає всі вчительські роутери"""

    return [
        AllWeekHandler().get_router(),
        MyPostHandler().get_router(),
        LessonsTodayHandler().get_router(),
        LessonsTomorrowHandler().get_router(),
        AcademyTime().get_router(),
        *get_olymp_router()
    ]
