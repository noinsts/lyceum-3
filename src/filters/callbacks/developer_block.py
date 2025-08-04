from enum import Enum

from aiogram.filters.callback_data import CallbackData


class DeveloperBlockEnum(str, Enum):
    BY_ID = "by_id"
    BY_TEACHER_NAME = "by_teacher_name"


class DeveloperBlockCallback(CallbackData, prefix="developer_block"):
    method: DeveloperBlockEnum
