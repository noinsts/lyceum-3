import datetime
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.db.connector import DBConnector


@dataclass(frozen=True)
class Messages:
    TITLE: str = (
        "<b>🌎 Цікава кнопка</b> - це кнопка, що оновлюється щодня і пропонує цікаву та корисну інформацію. "
        "Тут завжди можна знайти щось нове і несподіване, що зробить твій день трішки яскравішим."
    )

    NO_PROMPT: str = (
        "Отета да, схоже сьогодні нічого нового..."
    )


class InterestingButtonHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == '🌎 Цікава кнопка'
        )

    @classmethod
    async def handler(cls, message: Message, db: DBConnector) -> None:
        await message.answer(Messages.TITLE, parse_mode=ParseMode.HTML)
        prompt = await db.interesting.get_by_date(datetime.date.today())
        await message.answer(prompt or Messages.NO_PROMPT, parse_mode=ParseMode.HTML)
