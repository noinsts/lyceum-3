from enum import Enum

from aiogram.filters.callback_data import CallbackData


class BroadcastTypeEnum(str, Enum):
    STUDENT = "Учням"
    TEACHER = "Вчителям"
    ALL = "Взагалі всім"


class BroadcastTypeCallback(CallbackData, prefix="broadcast_type"):
    method: str
