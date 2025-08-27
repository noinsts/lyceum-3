from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.db.connector import DBConnector
from src.parsers.frontend import parse_day_name


class Triggers(str, Enum):
    TODAY = "📅 Класи на сьогодні"
    TOMORROW = "🌅 Розклад на завтра"


@dataclass(frozen=True)
class Messages:
    NO_TEACHER_NAME = (
        "⚠️ <b>Вибачте, вашого імені не ініціалізовано, будь-ласка, "
        "спробуйте повторно перереєструватись за допомогою команди /register</b>"
    )

    WEEKEND = (
        "🎉 Сьогодні — вихідний! Це ідеальний час, щоб відпочити та набратися сил. "
        "Насолоджуйтеся моментом! 😊"
    )

    NO_RESULTS = (
        "Ура! 🎉 На {day} у вас немає уроків. Можна видихнути й трохи відпочити!"
    )

    STICKER = "CAACAgIAAxkBAAEOZ1doFUn9Y0TR-qURiQeEb7HZdGC2qQACOjMAAlG5gEjH0Q7wxWFwrDYE"


class LessonsByDaysHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text.in_({Triggers.TODAY.value, Triggers.TOMORROW.value})
        )

    async def handler(self, message: Message, db: DBConnector) -> None:
        is_tomorrow = message.text == Triggers.TOMORROW.value
        offset = 1 if is_tomorrow else 0

        teacher_name = await db.register.get_teacher_name(message.from_user.id)

        if not teacher_name:
            await message.answer(Messages.NO_TEACHER_NAME, parse_mode=ParseMode.HTML)
            return

        day_name = parse_day_name(offset)

        day_word = "завтра" if is_tomorrow else "сьогодні"

        if not day_name:
            await message.answer(Messages.WEEKEND)
            await message.answer_sticker(Messages.STICKER)
            return

        sheet = await self.get_sheet()
        results = await sheet.teacher.get_lessons(teacher_name, day_name)

        if not results:
            await message.answer(Messages.NO_RESULTS.format(day=day_word))
            await message.answer_sticker(Messages.STICKER)
            return

        lessons_list = [f"<b>{lesson_id}</b>: {subject} з {form}" for lesson_id, subject, form in results]
        prompt = f'<b>Список класів на {day_word}</b>\n\n' + "\n".join(lessons_list)

        await message.answer(prompt, parse_mode=ParseMode.HTML)
