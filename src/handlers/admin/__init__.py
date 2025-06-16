from typing import List

from aiogram import Router

from .announcement_hub import AnnouncementHub
from .students_change_schedule import StudentsChangeSchedule
from .teachers_change_schedule import TeachersChangeSchedule


def get_admin_router() -> List[Router]:
    """Збір всіх адмінських роутерів"""
    return [
        AnnouncementHub().get_router(),
        StudentsChangeSchedule().get_router(),
        TeachersChangeSchedule().get_router()
    ]
