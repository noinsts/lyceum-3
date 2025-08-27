from enum import Enum

from aiogram.filters.callback_data import CallbackData


class TeacherVerifyEnum(str, Enum):
    HOW_GET = "Як отримати верифікацію"
    WHY_NEED = "Нащо це потрібно"
    HOW_WORKS = "Як це працює?"


class TeacherVerifyCallback(CallbackData, prefix="verify"):
    method: str
