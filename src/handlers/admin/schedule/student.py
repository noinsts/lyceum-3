from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler


class StudentsChangeSchedule(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'change_schedule_student'
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.message.answer("аче")

        # заглушка
        await callback.answer()
