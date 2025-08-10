from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.db.connector import DBConnector
from src.parsers.frontend import parse_day_name


class Triggers(str, Enum):
    TODAY_HANDLER = "📅 Розклад на сьогодні"
    TOMORROW_HANDLER = "🌇 Розклад на завтра"


@dataclass(frozen=True)
class Messages:
    NO_FORM = (
        r"Сьогодні хмарно\.\.\. ☁️ Спробуйте завтра 0\_0 ||або просто станьте учнем||"
    )

    WEEKEND = {
        'message': "Вихідний! Have a rest",
        'sticker': "CAACAgEAAxkBAAEOZSxoE3COqmuPY034826sWOvB7WgTQgACjgEAAnY3dj9180psDptQBzYE"
    }

    NO_RESULTS = (
        "Уроків немає, везе"
    )


class LessonsByDaysHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text.in_({Triggers.TODAY_HANDLER.value, Triggers.TOMORROW_HANDLER.value})
        )

    async def handler(self, message: Message, db: DBConnector) -> None:
        is_tomorrow = message.text == Triggers.TOMORROW_HANDLER.value
        offset = 1 if is_tomorrow else 0

        form = await db.register.get_form(message.from_user.id)

        if not form:
            await message.answer(Messages.NO_FORM, parse_mode=ParseMode.HTML)
            return

        day_name = parse_day_name(offset)

        if not day_name:
            await message.answer(Messages.WEEKEND['message'])
            await message.answer_sticker(Messages.WEEKEND['sticker'])
            return

        sheet = await self.get_sheet()
        results = await sheet.student.get_lessons(form, day_name)

        if not results:
            await message.answer(Messages.NO_RESULTS)
            return

        day_word = "завтра" if is_tomorrow else "сьогодні"
        lessons_list = [
            f"<b>{lesson_id}</b>: <b>{name}</b> з {teacher.replace(',', ' та')}\n\n"
            for lesson_id, name, teacher in results
        ]
        prompt = f"<b>Розклад уроків на {day_word}</b>\n\n" + "\n".join(lessons_list)

        await message.answer(prompt, parse_mode=ParseMode.HTML)
