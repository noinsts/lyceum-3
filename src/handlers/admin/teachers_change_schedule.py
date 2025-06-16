from aiogram import F
from aiogram.types import CallbackQuery

from ..base import BaseHandler


class TeachersChangeSchedule(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(self.teachers_change_schedule, F.data == 'teachers_change_schedule')

    @staticmethod
    async def teachers_change_schedule(callback: CallbackQuery) -> None:
        await callback.message.answer("аче")

        # заглушка
        await callback.answer()
