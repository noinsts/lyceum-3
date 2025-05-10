from collections import defaultdict
from datetime import datetime

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from .base import BaseHandler


class StudentHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.WEEKEND_STICKER = "CAACAgEAAxkBAAEOZSxoE3COqmuPY034826sWOvB7WgTQgACjgEAAnY3dj9180psDptQBzYE"
        self.WEEKEND_PROMPT = "Вихідний! Have a rest"
        # '\' для екранізування спец символів MD_V2
        self.NO_CLASS = r"Сьогодні хмарно\.\.\. ☁️ Спробуйте завтра 0\_0 ||або просто станьте учнем||"
        self.MASHA_SAD = "CAACAgIAAxkBAAEOaW5oF8pfixnPcAGhebO0hKOiCjBX2QAC3zQAAmJyiEvtgv45SmY1kzYE"


    def register_handler(self) -> None:
        self.router.message.register(self.today, F.text == '📅 Розклад на сьогодні')
        self.router.message.register(self.tomorrow, F.text == '🌇 Розклад на завтра')
        self.router.message.register(self.next_lesson, F.text == '➡️ Наступний урок')
        self.router.message.register(self.all_week, F.text == '📝 Розклад на весь тиждень')
        self.router.message.register(self.intresting_button, F.text == '🌎 Цікава кнопка')
        self.router.message.register(self.today_shorted, F.text == '❓ Сьогодні скорочені уроки?')


    async def intresting_button(self, message: Message) -> None:
        pass


    def _generate_schedule_message(self, day_name: str, results: list[tuple[int, str, str]], is_tomorrow: bool = False) -> str:
        day_type = "завтра" if is_tomorrow else "сьогодні"

        prompt = f"<b>Розклад уроків на {day_type} ({day_name.lower()})</b>:\n\n"

        for lesson_id, name, teacher in results:
            name, teacher = self.wf.student(name, teacher)
            if name:
                prompt += f"<b>{lesson_id}</b>: <b>{name}</b> з {teacher.replace(',', ' та')}\n\n"

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

        results = self.sheet.student.get_today(day_name, self.db.register.get_class(message.from_user.id))
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

        results = self.sheet.student.get_today(day_num, user_class)
        prompt = self._generate_schedule_message(day_num, results, is_tomorrow=True)

        await message.answer(prompt, parse_mode=ParseMode.HTML)


    async def next_lesson(self, message: Message) -> None:
        """Обробка кнопки ➡️ Наступний урок"""
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм
        user_class = self.db.register.get_class(message.from_user.id)

        if not user_class:
            await message.answer("Вибачте, інформації про вас не знайдено, скористайтесь командою /register")
            return

        day: int = message.date.astimezone(self.kyiv_tz).weekday()
        day: str = self.cfg._config.get(str(day))
        time = message.date.astimezone(self.kyiv_tz).time()

        # time = "08:29:00"
        #
        # await message.answer(
        #     f"DEBUG:\n\n"
        #     f"{time=}\n"
        #     f"{day=}"
        # )

        # time = datetime.strptime(time, "%H:%M:%S").time()

        results = self.sheet.student.next_lesson(day, user_class, time)
        get_day, l_num, to, subj, teach = results
        subj, teach = self.wf.student(subj, teach)

        prompt = [
            "<b>Наступний урок:</b>",
            "",
            f"#️⃣ {l_num} у {get_day.lower()}" if get_day != day else f"#️⃣ {l_num}",
            f"📄 {subj}",
            f"👨🏻‍🏫 {teach}",
            f"🕗 {self.tf.format_time_until(to)}"
        ]

        await message.answer(
            "\n".join(prompt),
            parse_mode=ParseMode.HTML
        )


    async def all_week(self, message: Message) -> None:
        user_class = self.db.register.get_class(message.from_user.id)
        results = self.sheet.student.all_week(user_class)

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


    async def today_shorted(self, message: Message) -> None:
        await message.answer("Я не знаю")
