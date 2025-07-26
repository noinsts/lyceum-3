from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler


class RefreshHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'refresh_cache_schedule'
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.message.answer("аче")

        await callback.answer()
