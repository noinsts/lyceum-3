from aiogram import F
from aiogram.types import CallbackQuery

from ..base import BaseHandler


class StudentsChangeSchedule(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(self.students_change_schedule, F.data == 'students_change_schedule')

    @staticmethod
    async def students_change_schedule(callback: CallbackQuery) -> None:
        await callback.message.answer("аче")

        # заглушка
        await callback.answer()
