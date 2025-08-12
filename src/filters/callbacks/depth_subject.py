from aiogram.filters.callback_data import CallbackData


class DepthSubjectCallback(CallbackData, prefix="depth_subject"):
    subject: str
