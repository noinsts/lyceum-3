from dataclasses import dataclass
from collections import defaultdict
from enum import Enum

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.db.connector import DBConnector
from src.parsers.frontend import parse_day_name
from src.utils import JSONLoader

WEEKDAYS = ('ПОНЕДІЛОК', 'ВІВТОРОК', 'СЕРЕДА', 'ЧЕТВЕР', "П'ЯТНИЦЯ")


class Triggers(str, Enum):
    WEEK_HANDLER = "📝 Розклад на весь тиждень"
    TODAY_HANDLER = "📅 Розклад на сьогодні"
    TOMORROW_HANDLER = "🌇 Розклад на завтра"


@dataclass(frozen=True)
class Messages:
    NO_FORM = (
        "Ойой, схоже, що виникла помилка. "
        "Спробуйте перереєструватись за допомогою команди /register"
    )

    NO_WEEK_RESULT = (
        "Поки що у тебе немає запланованих уроків на цей тиждень. Можливо, скоро з’являться!"
    )

    NO_DAY_RESULT = (
        "Щож, {} без уроків, дивно, чи не так?)"
    )

    WEEKEND = {
        'message': "Ура! Схоже, що у вас {day} вихідний",
        'sticker': "CAACAgEAAxkBAAEOZSxoE3COqmuPY034826sWOvB7WgTQgACjgEAAnY3dj9180psDptQBzYE"
    }

class ScheduleHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.week, F.text == Triggers.WEEK_HANDLER)
        self.router.message.register(self.day, F.text.in_({Triggers.TODAY_HANDLER, Triggers.TOMORROW_HANDLER}))

    async def week(self, message: Message, db: DBConnector) -> None:
        form = await db.register.get_form(message.from_user.id)

        if not form:
            await message.answer(Messages.NO_WEEK_RESULT)
            return

        sheet = await self.get_sheet()
        results = await sheet.student.get_lessons(form)

        if not results:
            await message.answer(Messages.NO_FORM)
            return

        lessons_by_days = defaultdict(list)
        for day, number, subject, teacher in results:
            lessons_by_days[day].append((number, subject, teacher))

        prompt = f"<b>Список уроків {form} класу</b>\n"

        # Орудні відмінки імен вчителів
        instrumental_names = JSONLoader("settings/instrumental_teacher_names.json")

        for day in WEEKDAYS:
            if day not in lessons_by_days:
                continue

            prompt += f"\n<b>{day.capitalize()}</b>\n"
            for number, subject, teacher in sorted(lessons_by_days[day]):
                teacher_names = [
                    instrumental_names.get(t.strip(), t.strip())
                    for t in teacher.split(',')
                ]

                teacher_string = " та ".join(teacher_names)
                prompt += f"<b>{number}</b>: {subject} з {teacher_string}\n"

        await message.answer(prompt, parse_mode=ParseMode.HTML)


    async def day(self, message: Message, db: DBConnector) -> None:
        is_tomorrow = message.text == Triggers.TOMORROW_HANDLER
        offset = 1 if is_tomorrow else 0

        form = await db.register.get_form(message.from_user.id)

        if not form:
            await message.answer(Messages.NO_FORM, parse_mode=ParseMode.HTML)
            return

        day = parse_day_name(offset)
        day_name = "завтра" if is_tomorrow else "сьогодні"

        if not day:
            await message.answer(Messages.WEEKEND['message'].format(day=day_name))
            await message.answer_sticker(Messages.WEEKEND['sticker'])
            return

        sheet = await self.get_sheet()
        results = await sheet.student.get_lessons(form, day)

        if not results:
            await message.answer(Messages.NO_DAY_RESULT.format(day=day_name))
            return

        lessons_list = [
            f"<b>{lesson_id}</b>: <b>{name}</b> з {teacher.replace(',', ' та')}"
            for lesson_id, name, teacher in results
        ]
        prompt = f"<b>Розклад уроків на {day_name}</b>\n\n" + "\n".join(lessons_list)

        await message.answer(prompt, parse_mode=ParseMode.HTML)
