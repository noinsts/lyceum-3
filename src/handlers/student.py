from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode
from pytz import timezone

from .base import BaseHandler
from src.settings.calls import Calls


class StudentHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.WEEKEND_STICKER = "CAACAgEAAxkBAAEOZSxoE3COqmuPY034826sWOvB7WgTQgACjgEAAnY3dj9180psDptQBzYE"
        self.WEEKEND_PROMPT = "Вихідний! Have a rest"
        # '\' для екранізування спец символів MD_V2
        self.NO_CLASS = r"Сьогодні хмарно\.\.\. ☁️ Спробуйте завтра 0\_0 ||або просто станьте учнем||"


    def register_handler(self) -> None:
        self.router.message.register(self.today, F.text == '📅 Розклад на сьогодні')
        self.router.message.register(self.tomorrow, F.text == '🌇 Розклад на завтра')
        self.router.message.register(self.next_lesson, F.text == '➡️ Наступний урок')
        self.router.message.register(self.calls, F.text == '🔔 Розклад дзвінків')


    @staticmethod
    def _generate_schedule_message(day_name: str, results: list[tuple[str]], is_tomorrow: bool = False) -> str:
        day_type = "завтра" if is_tomorrow else "сьогодні"

        prompt = f"Розклад уроків на {day_type} <b>({day_name.capitalize()})</b>:\n\n"

        for i, subject in enumerate(results):
            prompt += f"<b>{i+1}</b>: {subject[0]}\n"

        return prompt


    async def today(self, message: Message) -> None:
        """Обробка кнопки 📅 Розклад на сьогодні"""
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        user_class = self.db.register.get_class(message.from_user.id)

        if not user_class:
            await message.answer(self.NO_CLASS, parse_mode=ParseMode.MARKDOWN_V2)
            return

        # визначення дня за повідомленням
        day_num: int = message.date.astimezone(self.kyiv_tz).weekday()

        # Перевірка, чи це будній день
        if day_num > 4:
            await message.answer(self.WEEKEND_PROMPT)
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        # перетворення для обчислень в бд
        day_name = self.cfg._config.get(str(day_num))

        results = self.db.student.get_today(day_name, self.db.register.get_class(message.from_user.id))
        prompt = self._generate_schedule_message(day_name, results)

        await message.answer(prompt, parse_mode=ParseMode.HTML)


    async def tomorrow(self, message: Message) -> None:
        """Обробка кнопки 🌇 Розклад на завтра"""
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        user_class = self.db.register.get_class(message.from_user.id)

        if not user_class:
            await message.answer(self.NO_CLASS, parse_mode=ParseMode.MARKDOWN_V2)
            return

        # обчислення дня за повідомленням
        day_num: int = message.date.astimezone(self.kyiv_tz).weekday()

        # обчислення завтрашнього дня
        day_num: int = 0 if day_num == 6 else day_num + 1


        # перевірка, чи це будній день
        if day_num > 4:
            await message.answer(self.WEEKEND_PROMPT)
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        # перетворення дня для бд
        day_num: str = self.cfg._config.get(str(day_num))

        results = self.db.student.get_today(day_num, user_class)
        prompt = self._generate_schedule_message(day_num, results, is_tomorrow=True)

        await message.answer(prompt, parse_mode=ParseMode.HTML)


    async def next_lesson(self, message: Message) -> None:
        """Обробка кнопки ➡️ Наступний урок"""
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        await message.answer("Поки що в розробці 🌚")


    async def calls(self, message: Message) -> None:
        """Обробник кнопки 🔔 Розклад дзвінків"""
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        data = Calls().CALLS

        prompt = f"🔔 <b>Розклад дзвінків</b>\n\n"

        for date, name in data.items():
            prompt += f"<b>{date}</b> — {name}\n"

        await message.answer(prompt, parse_mode=ParseMode.HTML)
