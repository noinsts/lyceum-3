from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode
from pytz import timezone

from ..base import BaseHandler
from src.db.connector import DBConnector


class Triggers(str, Enum):
    HANDLER = "❓ Сьогодні скорочені уроки?"


@dataclass(frozen=True)
class Messages:
    DEFAULT: str = (
        "Сьогодні звичайні уроки"
    )

    SHORTENED: str = (
        "<b>Сьогодні скорочені уроки</b> 🎉\n\n"
        "{call_schedule}"
    )


KYIV_TZ = timezone("Europe/Kyiv")


class TodayShortenedHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == Triggers.HANDLER
        )

    @staticmethod
    async def handler(message: Message, db: DBConnector) -> None:
        date = message.date.astimezone(KYIV_TZ).date()
        day = await db.shortened.get_day(date)
        await message.answer(
            Messages.SHORTENED.format(day.call_schedule)
            if day and day.status else Messages.DEFAULT,
            parse_mode=ParseMode.HTML
        )
