from collections import defaultdict
from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.utils import JSONLoader
from src.db.connector import DBConnector

WEEKDAYS = ('ПОНЕДІЛОК', 'ВІВТОРОК', 'СЕРЕДА', 'ЧЕТВЕР', "П'ЯТНИЦЯ")


class Triggers(str, Enum):
    HANDLER = "📝 Розклад на весь тиждень"


@dataclass(frozen=True)
class Messages:
    NO_FORM = (
        "Вашого класу немає в БД. Будь-ласка зареєструйтесь знову, "
        "використовуючи команду /register"
    )

    NO_RESULT = (
        "У вас немає уроків.Дивно, правда?)"
    )


class AllWeekHandler(BaseHandler):
    def register_handler(self):
        self.router.message.register(
            self.all_week,
            F.text == Triggers.HANDLER
        )

    async def all_week(self, message: Message, db: DBConnector) -> None:
        """
        Обробка відправлення студенту розкладу на весь тиждень
        """
        user_form = await db.register.get_form(message.from_user.id)

        if not user_form:
            await message.answer(Messages.NO_FORM)
            return

        sheet = await self.get_sheet()
        results = await sheet.student.get_lessons(user_form)

        if not results:
            await message.answer(Messages.NO_RESULT)
            return

        # сортуємо по днях
        lessons_by_day = defaultdict(list)
        for day, number, subject, teacher in results:
            lessons_by_day[day].append((number, subject, teacher))

        prompt = f"<b>Список уроків {user_form} класу</b>\n"

        # завантажуємо файл з орудними відмінками
        instrumental_names = JSONLoader("settings/instrumental_teacher_names.json")

        for day in WEEKDAYS:
            if day not in lessons_by_day:
                continue

            prompt += f"\n<b>{day.capitalize()}</b>\n"
            for number, subject, teacher in sorted(lessons_by_day[day]):
                teacher_names = [
                    instrumental_names.get(t.strip(), t.strip())
                    for t in teacher.split(',')
                ]

                teacher_string = " та ".join(teacher_names)
                prompt += f"<b>{number}</b>: {subject} з {teacher_string}\n"

        await message.answer(prompt, parse_mode=ParseMode.HTML)
