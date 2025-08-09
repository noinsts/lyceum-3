from typing import List

from aiogram import Router

from .hub import AdminScheduleHub
from .student import StudentsChangeSchedule
from .teacher import TeachersChangeSchedule
from .refresh import RefreshHandler
from .cache_stats import CacheStatsHandler


def get_admin_schedule_routers() -> List[Router]:
    """Повертає список адмінських роутерів для розкладу"""
    return [
        AdminScheduleHub().get_router(),
        StudentsChangeSchedule().get_router(),
        TeachersChangeSchedule().get_router(),
        RefreshHandler().get_router(),
        CacheStatsHandler().get_router()
    ]
