from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from .base import BaseHandler
from settings.calls import Calls


class AllHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.calls, F.text == '🔔 Розклад дзвінків')


    async def calls(self, message: Message) -> None:
        """Обробник кнопки 🔔 Розклад дзвінків"""
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        data = Calls().CALLS

        prompt = "🔔 <b>Розклад дзвінків</b>\n\n"

        for date, name in data.items():
            prompt += f"<b>{date}</b> — {name}\n"

        await message.answer(prompt, parse_mode=ParseMode.HTML)
