from aiogram import F
from aiogram.types import Message

from src.handlers.base import BaseHandler


class TodayShortedHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.today_shorted,
            F.text == '❓ Сьогодні скорочені уроки?'
        )

    @staticmethod
    async def today_shorted(message: Message) -> None:
        await message.answer("Я не знаю")
