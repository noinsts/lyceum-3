from collections import Counter, defaultdict
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.parsers.backend import ScheduleParsers
from src.db.connector import DBConnector


WEEKDAYS = ('ПОНЕДІЛОК', 'ВІВТОРОК', 'СЕРЕДА', 'ЧЕТВЕР', "П'ЯТНИЦЯ")


class Triggers(str, Enum):
    HANDLER = "⏰ Кількість академічних годин"


@dataclass(frozen=True)
class Messages:
    NO_RESULTS = "Схоже, що цього тижня уроків у вас немає."

    TITLE = "⏰ <b>Кількість академічних годин на тиждень</b>"



class AcademyTimeHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.academy_time,
            F.text == Triggers.HANDLER
        )

    async def academy_time(self, message: Message, db: DBConnector) -> None:
        """
        Обробка кнопки "⏰ Кількість академічних годин"

        Args:
            message: Повідомлення користувача

        Returns:
            Академічні години для кожного дня та для всього тижня
        """

        tn = await db.register.get_teacher_name(message.from_user.id)

        sheet = await self.get_sheet()
        results = await sheet.teacher.get_lessons(tn)

        if not results:
            await message.answer(Messages.NO_RESULTS)
            return

        count_by_day, total = self._count_academic_hours(results)

        wf = "чисельником" if ScheduleParsers.week() == 0 else "знаменником"

        lines = [
            Messages.TITLE,
            f"<i>за {wf}</i>\n"
        ]

        for day in WEEKDAYS:
            if day not in count_by_day:
                continue

            count = count_by_day[day]
            lines.append(f"<b>{day.capitalize()}</b>: {count} академ. годин")

        lines.append(f"\n<b>Всього за тиждень</b>: {total} год.")

        prompt = "\n".join(lines)
        await message.answer(prompt, parse_mode=ParseMode.HTML)

    @classmethod
    def _count_academic_hours(cls, lessons: List[Tuple]) -> Tuple[defaultdict[str, int], int]:
        days = (day for day, *_ in lessons)
        count_by_day = Counter(days)
        total = sum(count_by_day.values())
        return defaultdict(int, count_by_day), total
