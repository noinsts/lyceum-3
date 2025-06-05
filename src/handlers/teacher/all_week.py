from collections import defaultdict

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler


class AllWeekHandler(BaseHandler):
    def register_handler(self):
        self.router.message.register(self.all_week, F.text == '📝 Тижневий розклад')

    async def all_week(self, message: Message) -> None:
        tn = self.db.register.get_teacher_name(message.from_user.id)
        results = self.db.teacher.get_all_week(tn)

        by_day = defaultdict(list)

        for day, lesson_id, subject, form in results:
            by_day[day].append((lesson_id, subject, form))

        prompt = "<b>Розклад на тиждень</b>\n\n"

        for day, lessons in by_day.items():
            prompt += f"\n<b>{day.capitalize()}</b>\n"
            for number, subject, form in lessons:
                prompt += f"<b>{number}</b>: {subject} з {form}\n"

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )
