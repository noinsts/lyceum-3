from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler


class Triggers:
    """Клас з тригерами callback"""
    HANDLER = "dev_access_stats"


class Messages:
    """Клас з константами для повідомлень"""
    MESSAGE = "⏳ Наберіться терпіння! Ми працюємо над цим розділом."


class StatsAccessHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.answer(Messages.MESSAGE, show_alert=True)
