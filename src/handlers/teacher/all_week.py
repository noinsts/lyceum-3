from collections import defaultdict
from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.db.connector import DBConnector

WEEKDAYS = ('ПОНЕДІЛОК', 'ВІВТОРОК', 'СЕРЕДА', 'ЧЕТВЕР', "П'ЯТНИЦЯ")


class Triggers(str, Enum):
    HANDLER = "📝 Тижневий розклад"


@dataclass(frozen=True)
class Messages:
    NO_RESULTS = (
        "Схоже, у вас цього тижня немає жодного уроку. "
        "Вітаю, ви або в відпустці, або дуже щасливий викладач 😎"
    )


class AllWeekHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.all_week,
            F.text == Triggers.HANDLER.value
        )

    async def all_week(self, message: Message, db: DBConnector) -> None:
        teacher_name = await db.register.get_teacher_name(message.from_user.id)

        sheet = await self.get_sheet()
        results = await sheet.teacher.get_lessons(teacher_name)

        if not results:
            await message.answer(Message.NO_RESULTS)
            return

        by_day = defaultdict(list)

        for day, lesson_id, subject, form in results:
            by_day[day].append((lesson_id, subject, form))

        prompt = "<b>Розклад на тиждень</b>\n\n"

        for day in WEEKDAYS:
            if day not in by_day:
                continue

            prompt += f"\n<b>{day.capitalize()}</b>\n"

            for number, subject, form in sorted(by_day[day]):
                prompt += f"<b>{number}</b>: {subject} з {form}\n"

        await message.answer(prompt, parse_mode=ParseMode.HTML)
