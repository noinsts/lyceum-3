from enum import Enum

from aiogram.filters.callback_data import CallbackData


class DeveloperSearchEnum(str, Enum):
    BY_ID = "by_id"
    BY_TEACHER_NAME = "by_teacher_name"


class DeveloperSearchCallback(CallbackData, prefix="developer_block"):
    method: DeveloperSearchEnum
