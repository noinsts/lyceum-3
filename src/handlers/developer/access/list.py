from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler


class ListAccessHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'dev_access_list'
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.answer("Поки не готово...")
