from dataclasses import dataclass
from enum import Enum

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode
from pytz import timezone

from ..base import BaseHandler
from settings.calls import Calls
from src.db.connector import DBConnector


class Triggers(str, Enum):
    HANDLER = "🔔 Розклад дзвінків"


@dataclass(frozen=True)
class Messages:
    TITLE: str = "🔔 <b>Розклад дзвінків</b>\n\n"


KYIV_TZ = timezone("Europe/Kyiv")


class CallsHandler(BaseHandler):
    def register_handler(self):
        self.router.message.register(self.handler, F.text == Triggers.HANDLER)

    async def handler(self, message: Message, db: DBConnector) -> None:
        """Обробник кнопки 🔔 Розклад дзвінків"""
        date = message.date.astimezone(KYIV_TZ).date()
        day = await db.day.get_day(date)

        schedule = day.call_schedule if day and day.call_schedule else self._get_default_schedule()
        text = f"{Messages.TITLE}{schedule}"

        await message.answer(text, parse_mode=ParseMode.HTML)

    @staticmethod
    def _get_default_schedule() -> str:
        return "\n".join(f"<b>{date}</b> — {name}" for date, name in Calls().CALLS.items())
