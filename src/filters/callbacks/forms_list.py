from aiogram.filters.callback_data import CallbackData


class FormsListCallback(CallbackData, prefix="form"):
    form: str
