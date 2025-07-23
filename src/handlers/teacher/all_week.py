from collections import defaultdict

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.db.connector import DBConnector

WEEKDAYS = ('ПОНЕДІЛОК', 'ВІВТОРОК', 'СЕРЕДА', 'ЧЕТВЕР', "П'ЯТНИЦЯ")


class AllWeekHandler(BaseHandler):
    def register_handler(self):
        self.router.message.register(self.all_week, F.text == '📝 Тижневий розклад')

    async def all_week(self, message: Message, db: DBConnector) -> None:
        teacher_name = await db.register.get_teacher_name(message.from_user.id)
        results = self.sheet.teacher.get_lessons(teacher_name)

        if not results:
            await message.answer(
                "Схоже, у вас цього тижня немає жодного уроку. "
                "Вітаю, ви або в відпустці, або дуже щасливий викладач 😎"
            )
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

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )
