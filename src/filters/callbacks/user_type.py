from aiogram.filters.callback_data import CallbackData


class UserTypeCallback(CallbackData, prefix="user_type"):
    utype: str
