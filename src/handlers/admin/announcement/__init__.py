from typing import List

from aiogram import Router


from .hub import AnnouncementHub
from .meeting import MeetingHandler


def get_announcement_router() -> List[Router]:
    """Повертає список оголошувальних адмінських роутерів"""
    return [
        AnnouncementHub().get_router(),
        MeetingHandler().get_router()
    ]
