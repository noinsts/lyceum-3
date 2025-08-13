from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from src.handlers.base import BaseHandler


class InterestingButtonHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == '🌎 Цікава кнопка'
        )

    @staticmethod
    async def handler(message: Message) -> None:
        interesting_button = (
            "<b>🌎 Цікава кнопка</b> - це кнопка, що оновлюється щодня і пропонує цікаву та корисну інформацію. "
            "Тут завжди можна знайти щось нове і несподіване, що зробить твій день трішки яскравішим."
        )

        prompt = (
            "<b>Мало хто знає, але Остапенко Михайло за це літо був три рази ведучим</b>\n\n"
            "🔹 на випускному 9-х класів\n"
            "🔹 на випускному 11-х класів\n"
            "🔹 в Пулласі (Німеччина)\n\n"
            "<i>7/27/2025 — Андрій (noinsts)</i>"
        )

        await message.answer(interesting_button, parse_mode=ParseMode.HTML)
        await message.answer(prompt, parse_mode=ParseMode.HTML)
