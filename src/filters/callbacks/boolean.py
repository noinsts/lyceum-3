from aiogram.filters.callback_data import CallbackData


class BooleanCallback(CallbackData, prefix="boolean"):
    boolean: bool
