from aiogram.filters.callback_data import CallbackData


class TeacherListCallback(CallbackData, prefix="teacher_"):
    teacher_id: int
