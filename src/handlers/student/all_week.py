from collections import defaultdict

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler

class AllWeekHandler(BaseHandler):
     def register_handler(self):
          self.router.message.register(self.all_week, F.text == '📝 Розклад на весь тиждень')

     async def all_week(self, message: Message) -> None:
        user_class = self.db.register.get_class(message.from_user.id)
        results = self.sheet.student.get_lessons(user_class)

        lessons_by_day = defaultdict(list)

        # додаємо дані в lessons_by_day
        for day, number, subject, teacher in results:
            lessons_by_day[day].append((number, subject, teacher))

        prompt = f"<b>Список уроків {user_class} класу</b>\n"

        # зчитуємо та виводимо дані
        for day, lessons in lessons_by_day.items():
            prompt += f"\n<b>{day.capitalize()}</b>\n"
            for number, subject, teacher in lessons:
                subject, teacher = self.wf.student(subject, teacher)
                if subject:
                    prompt += f"<b>{number}</b>: {subject} з {teacher.replace(",", " та")}\n"

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )
