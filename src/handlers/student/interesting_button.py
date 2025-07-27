from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from handlers.base import BaseHandler


class InterestingButtonHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == '🌎 Цікава кнопка'
        )

    @staticmethod
    async def handler(message: Message) -> None:
        prompt = (
            "<b>Мало хто знає, але Остапенко Михайло за це літо був три рази ведучим</b>\n\n"
            "🔹 на випускному 9-х класів\n"
            "🔹 на випускному 11-х класів\n"
            "🔹 в Пулласі (Німеччина)\n\n"
            "<i>7/27/2025 — Андрій (noinsts)</i>"
        )

        await message.answer(prompt, parse_mode=ParseMode.HTML)
