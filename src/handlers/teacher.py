from collections import defaultdict

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types import Message

from .base import BaseHandler

class TeacherHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.WEEKEND_PROMPT = "Сьогодні вихідний! Чому ви думаєте про роботу? Може краще відпочити 🙂‍↕️"
        self.WEEKEND_STICKER = "CAACAgIAAxkBAAEOZ1doFUn9Y0TR-qURiQeEb7HZdGC2qQACOjMAAlG5gEjH0Q7wxWFwrDYE"
        self.HAPPY_GUY = "CAACAgIAAxkBAAEOZ1loFUxiV3fJxTbJ0Q6iD6LDAkhsxwACBTgAAp17sEknYmmEwwt6pTYE"


    def register_handler(self) -> None:
        self.router.message.register(self.my_post, F.text == '🚦 Мій пост')
        self.router.message.register(self.lessons_today, F.text == '📅 Класи на сьогодні')
        self.router.message.register(self.all_week, F.text == '📝 Тижневий розклад')
        self.router.message.register(self.lessons_tomorrow, F.text == '🌅 Розклад на завтра')


    async def my_post(self, message: Message) -> None:
        """Обробник кнопки 🚦 Мій пост"""
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        week_name: int = message.date.astimezone(self.kyiv_tz).weekday()

        # обробка події, якщо день відправлення - вихідний
        if week_name > 4:
            await message.answer(self.WEEKEND_PROMPT)
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        week_name: str = self.cfg._config.get(str(week_name))
        teacher_name = self.db.register.get_teacher_name(message.from_user.id)

        if not teacher_name:
            await message.answer(
                "⚠️ <b>Вибачте, вашого імені не ініціалізовано, будь-ласка, "
                "спробуйте повторно перереєструватись за допомогою команди /register</b>",
                parse_mode=ParseMode.HTML
            )
            return

        result = self.db.teacher.get_post(week_name, teacher_name)

        if not result:
            await message.answer("Вам пощастило! Сьогодні ви не прив'язані до посту, можете відпочити")
            await message.answer_sticker(self.HAPPY_GUY)
            return

        await message.answer(
            f"Не пощастило \n\n"
            f"Сьогодні у вас запланове чергування на \"<b>{result}</b>\"",
            parse_mode=ParseMode.HTML
        )


    def _generate_message(self, results, is_tomorrow: bool = False) -> str:
        day = "завтра" if is_tomorrow else "сьогодні"
        prompt = f'<b>Список класів на {day}</b>\n\n'

        # TODO: зробить інформацію про ще одного вчителя з яким проходить урок (друга підгрупа)
        # TODO: робимо перевірку чи є два split(',')
        # TODO: якщо є, то знаходимо де вчитель != імені вчителя клієнта
        # TODO: виводимо цю частину teacher в schedule

        for lesson_id, subject, form in results:
            prompt += f"<b>{lesson_id}</b>: {subject} з {form}\n"

        prompt += "\n<i>Знайшли неточність? Будь-ласка повідомте @noinsts</i>"

        return prompt


    async def lessons_today(self, message: Message) -> None:
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        week_name: int = message.date.astimezone(self.kyiv_tz).weekday()

        # обробка події, якщо день відправлення - вихідний
        if week_name > 4:
            await message.answer(self.WEEKEND_PROMPT)
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        week_name: str = self.cfg._config.get(str(week_name))
        teacher_name = self.db.register.get_teacher_name(message.from_user.id)


        if not teacher_name:
            await message.answer(
                "⚠️ <b>Вибачте, вашого імені не ініціалізовано, будь-ласка, "
                "спробуйте повторно перереєструватись за допомогою команди /register</b>",
                parse_mode=ParseMode.HTML
            )
            return

        results = self.sheet.teacher.get_lessons_today(week_name, teacher_name)

        if not results:
            await message.answer("Сьогодні у вас вихідний!")
            await message.answer_sticker(self.HAPPY_GUY)
            return

        prompt = self._generate_message(results)

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )


    async def lessons_tomorrow(self, message: Message) -> None:
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        week_name: int = message.date.astimezone(self.kyiv_tz).weekday() + 1

        # обробка події, якщо день відправлення - вихідний
        if week_name > 4:
            await message.answer(self.WEEKEND_PROMPT)
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        week_name: str = self.cfg._config.get(str(week_name))
        teacher_name = self.db.register.get_teacher_name(message.from_user.id)

        if not teacher_name:
            await message.answer(
                "⚠️ <b>Вибачте, вашого імені не ініціалізовано, будь-ласка, "
                "спробуйте повторно перереєструватись за допомогою команди /register</b>",
                parse_mode=ParseMode.HTML
            )
            return

        results = self.sheet.teacher.get_lessons_today(teacher_name, week_name)

        if not results:
            await message.answer("Завтра у вас вихідний!")
            await message.answer_sticker(self.HAPPY_GUY)
            return

        prompt = self._generate_message(results, is_tomorrow=True)

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )


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
