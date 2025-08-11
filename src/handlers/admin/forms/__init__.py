from typing import List

from aiogram import Router

from .get_info import GetFormInfoHandler
from .hub import FormHubHandler
from .set_form_teacher import SetFormTeacherHandler
from .set_depth import SetDepthSubjectHandler


def get_form_admin_routers() -> List[Router]:
    """Повертає список адмінських роутерів для керування класами"""
    return [
        FormHubHandler().get_router(),
        GetFormInfoHandler().get_router(),
        SetFormTeacherHandler().get_router(),
        SetDepthSubjectHandler().get_router()
    ]
