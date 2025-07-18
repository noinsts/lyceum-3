from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.utils import JSONLoader
from src.sheets.connector import Sheet
from src.db.connector import DBConnector


class GenerateMessage:
    @staticmethod
    async def send(message: Message, tn: str, offset: int = 0, tz = None) -> None:

        if not tn:
            # оброблюємо ситуацію, коли вчитель не зареєстрований
            await message.answer(
                "⚠️ <b>Вибачте, вашого імені не ініціалізовано, будь-ласка, "
                "спробуйте повторно перереєструватись за допомогою команди /register</b>",
                parse_mode=ParseMode.HTML
            )
            return

        day_num: int = (message.date.astimezone(tz).weekday() + offset) % 7

        if day_num > 4:
            # оброблюємо ситуацію, якщо вихідний
            await message.answer("Вихідний! Чому ви думаєте про роботу?")
            await message.answer_sticker("CAACAgIAAxkBAAEOZ1doFUn9Y0TR-qURiQeEb7HZdGC2qQACOjMAAlG5gEjH0Q7wxWFwrDYE")
            return
        
        day_name: str = JSONLoader("settings/ukranian_weekname.json").get(str(day_num))

        results = Sheet().teacher.get_lessons(tn, day_name)

        if not results:
            # оброблюємо ситуацію, коли у вчителя вихідний
            await message.answer("Вам пощастило! Уроків немає")
            await message.answer_sticker("CAACAgIAAxkBAAEOZ1loFUxiV3fJxTbJ0Q6iD6LDAkhsxwACBTgAAp17sEknYmmEwwt6pTYE")
            return
        
        prompt = f'<b>Список класів на {"завтра" if offset > 0 else "сьогодні"}</b>\n\n'

        # TODO: зробить інформацію про ще одного вчителя з яким проходить урок (друга підгрупа)
        # TODO: робимо перевірку чи є два split(',')
        # TODO: якщо є, то знаходимо де вчитель != імені вчителя клієнта
        # TODO: виводимо цю частину teacher в schedule

        for lesson_id, subject, form in results:
            prompt += f"<b>{lesson_id}</b>: {subject} з {form}\n"

        prompt += "\n<i>Знайшли неточність? Будь-ласка повідомте @noinsts</i>"

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )
            

class LessonsTodayHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.today, F.text == '📅 Класи на сьогодні')

    async def today(self, message: Message, db: DBConnector) -> None:
        tn = await db.register.get_teacher_name(message.from_user.id)
        await GenerateMessage().send(message, tn, 0, self.kyiv_tz)


class LessonsTomorrowHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.tomorrow, F.text == '🌅 Розклад на завтра')

    async def tomorrow(self, message: Message, db: DBConnector) -> None:
        tn = await db.register.get_teacher_name(message.from_user.id)
        await GenerateMessage().send(message, tn, 1, self.kyiv_tz)
