from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler


class EditOlympHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'edit_olymp'
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.answer("Поки не працює...")
