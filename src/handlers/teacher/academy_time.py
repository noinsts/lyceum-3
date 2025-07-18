from collections import defaultdict

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.utils import WeekFormat
from src.db.connector import DBConnector


class AcademyTime(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.academy_time, F.text == '⏰ Кількість академічних годин')

    async def academy_time(self, message: Message, db: DBConnector) -> None:
        """
        Обробка кнопки "⏰ Кількість академічних годин"

        Args:
            message: Повідомлення користувача

        Returns:
            Академічні години для кожного дня та для всього тижня
        """

        tn = await db.register.get_teacher_name(message.from_user.id)
        results = self.sheet.teacher.get_lessons(tn)

        count_by_day = defaultdict(int)

        for day, _, _, _ in results:
            count_by_day[day] += 1

        prompt = "⏰ <b>Кількість академічних годин на тиждень</b>\n"

        wf = "чисельником" if WeekFormat().week() == 0 else "знаменником"
        prompt += f"<i>за {wf}</i>\n\n"

        for day, count in count_by_day.items():
            prompt += f"<b>{day.capitalize()}</b>: {count} академ. годин\n"

        prompt += f"\n<b>Всього за тиждень</b>: {len(results)} год."

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )
