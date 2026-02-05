from enum import Enum
from collections import defaultdict
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.db.connector import DBConnector
from src.parsers.frontend import parse_day_name

WEEKDAYS = ('ПОНЕДІЛОК', 'ВІВТОРОК', 'СЕРЕДА', 'ЧЕТВЕР', "П'ЯТНИЦЯ")


class Triggers(str, Enum):
    TODAY_HANDLER = "📅 Класи на сьогодні"
    TOMORROW_HANDLER = "🌅 Розклад на завтра"
    WEEK_HANDLER = "📝 Тижневий розклад"


@dataclass(frozen=True)
class Messages:
    NO_TEACHER_ERROR = (
        "⚠️ <b>Вибачте, вас не ініціалізовано, будь-ласка, "
        "спробуйте повторно перереєструватись за допомогою команди /register</b>"
    )

    NO_WEEK_RESULTS = (
        "Схоже, у вас цього тижня немає жодного уроку. "
        "Вітаю, ви або в відпустці, або дуже щасливий викладач 😎"
    )

    WEEKEND = (
        "🎉 {day} — вихідний! Це ідеальний час, щоб відпочити та набратися сил. "
        "Насолоджуйтеся моментом! 😊"
    )

    NO_DAY_RESULTS = (
        "Ура! 🎉 На {day} у вас немає уроків. Можна видихнути й трохи відпочити!"
    )

    HAPPY_STICKER = "CAACAgIAAxkBAAEOZ1doFUn9Y0TR-qURiQeEb7HZdGC2qQACOjMAAlG5gEjH0Q7wxWFwrDYE"



class ScheduleHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.week, F.text == Triggers.WEEK_HANDLER)
        self.router.message.register(self.day, F.text.in_({Triggers.TODAY_HANDLER, Triggers.TOMORROW_HANDLER}))

    async def week(self, message: Message, db: DBConnector) -> None:
        teacher_name = await db.register.get_teacher_name(message.from_user.id)

        if not teacher_name:
            await message.answer(Messages.NO_TEACHER_ERROR)
            return

        sheet = await self.get_sheet()
        results = await sheet.teacher.get_lessons(teacher_name)

        if not results:
            await message.answer(Messages.NO_WEEK_RESULTS)
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

    async def day(self, message: Message, db: DBConnector) -> None:
        is_tomorrow = message.text == Triggers.TOMORROW_HANDLER
        offset = 1 if is_tomorrow else 0

        teacher_name = await db.register.get_teacher_name(message.from_user.id)

        if not teacher_name:
            await message.answer(Messages.NO_TEACHER_ERROR)
            return

        day_name = parse_day_name(offset)
        day_word = "завтра" if is_tomorrow else "сьогодні"

        if not day_name:
            await message.answer(Messages.WEEKEND.format(day=day_name, day_word=day_word))
            await message.answer_sticker(Messages.HAPPY_STICKER)
            return

        sheet = await self.get_sheet()
        results = await sheet.teacher.get_lessons(teacher_name, day_name)

        if not results:
            await message.answer(Messages.NO_DAY_RESULTS)
            await message.answer_sticker(Messages.HAPPY_STICKER)
            return

        lessons_list = [f"<b>{lesson_id}</b>: {subject} з {form}" for lesson_id, subject, form in results]
        prompt = f'<b>Список класів на {day_word}</b>\n\n' + "\n".join(lessons_list)

        await message.answer(prompt, parse_mode=ParseMode.HTML)
