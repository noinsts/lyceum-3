from aiogram.filters.callback_data import CallbackData


class TeacherCategoryCallback(CallbackData, prefix="teacher_type"):
    name: str
