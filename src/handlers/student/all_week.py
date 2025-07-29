from collections import defaultdict

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.utils import JSONLoader
from src.db.connector import DBConnector

WEEKDAYS = ('ПОНЕДІЛОК', 'ВІВТОРОК', 'СЕРЕДА', 'ЧЕТВЕР', "П'ЯТНИЦЯ")


class AllWeekHandler(BaseHandler):
    def register_handler(self):
        self.router.message.register(self.all_week, F.text == '📝 Розклад на весь тиждень')

    async def all_week(self, message: Message, db: DBConnector) -> None:
        """
        Обробка відправлення студенту розкладу на весь тиждень
        """

        user_class = await db.register.get_form(message.from_user.id)
        results = self.sheet.student.get_lessons(user_class)

        if not results:
            await message.answer("У вас немає уроків. Дивно, правда?)")
            return

        # сортуємо по днях
        lessons_by_day = defaultdict(list)
        for day, number, subject, teacher in results:
            lessons_by_day[day].append((number, subject, teacher))

        # початок повідомлення
        prompt = f"<b>Список уроків {user_class} класу</b>\n"

        # завантажуємо файл з орудними відмінками
        instrumental_names = JSONLoader("settings/instrumental_teacher_names.json")

        for day in WEEKDAYS:
            if day not in lessons_by_day:
                continue

            prompt += f"\n<b>{day.capitalize()}</b>\n"
            for number, subject, teacher in sorted(lessons_by_day[day]):
                # парсимо дані відповідно до тижня
                subject, teacher = self.wf.student(subject, teacher)

                if not subject:
                    continue

                # TODO: винести парсер в окремий файл
                # парсомо імена вчителів за орудним відмінком
                teacher_names = [
                    instrumental_names.get(t.strip(), t.strip())
                    for t in teacher.split(',')
                ]

                teacher_string = " та ".join(teacher_names)
                prompt += f"<b>{number}</b>: {subject} з {teacher_string}\n"

        # виводимо дані
        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )
