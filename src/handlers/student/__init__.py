from typing import List

from aiogram import Router

from .all_week import AllWeekHandler
from .lessons_by_day import LessonsTodayHandler, LessonsTomorrowHandler
from .next_lesson import NextLessonHandler

def get_student_router() -> List[Router]:
    """Збір всіх роутерів student"""
    
    return [
        AllWeekHandler().get_router(),
        LessonsTodayHandler().get_router(),
        LessonsTomorrowHandler().get_router(),
        NextLessonHandler().get_router()
    ]
