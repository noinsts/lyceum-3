from aiogram import F
from aiogram.types import Message

from ..base import BaseHandler

class TodayShortedHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.today_shorted, F.text == '❓ Сьогодні скорочені уроки?')

    async def today_shorted(self, message: Message) -> None:
        await message.answer("Я не знаю")

