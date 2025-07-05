from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler


class ListOlympsHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'list_olymps'
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.answer("Поки не працює...")
