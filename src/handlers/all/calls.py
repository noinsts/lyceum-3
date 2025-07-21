from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from settings.calls import Calls


class CallsHandler(BaseHandler):
    def register_handler(self):
        self.router.message.register(self.calls, F.text == '🔔 Розклад дзвінків')

    @staticmethod
    async def calls(message: Message) -> None:
        """Обробник кнопки 🔔 Розклад дзвінків"""
        data = Calls().CALLS

        prompt = "🔔 <b>Розклад дзвінків</b>\n\n"

        for date, name in data.items():
            prompt += f"<b>{date}</b> — {name}\n"

        await message.answer(prompt, parse_mode=ParseMode.HTML)
