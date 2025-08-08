# FIXME: не працює

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types import Message

from ..base import BaseHandler
from src.db.connector import DBConnector


class MyPostHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        # Константи для стікерів та повідомлень
        self.WEEKEND_PROMPT = "вихідний! Чому ви думаєте про роботу? Може краще відпочити 🙂‍↕️"
        self.WEEKEND_STICKER = "CAACAgIAAxkBAAEOZ1doFUn9Y0TR-qURiQeEb7HZdGC2qQACOjMAAlG5gEjH0Q7wxWFwrDYE"
        self.HAPPY_GUY = "CAACAgIAAxkBAAEOZ1loFUxiV3fJxTbJ0Q6iD6LDAkhsxwACBTgAAp17sEknYmmEwwt6pTYE"

    def register_handler(self) -> None:
        self.router.message.register(self.handler, F.text == '🚦 Мій пост')

    @staticmethod
    async def handler(message: Message) -> None:
        await message.answer("Функція стане доступною після отримання графіку чергування 2025-2026 н. р.")

    async def my_post(self, message: Message, db: DBConnector) -> None:
        """Обробник кнопки 🚦 Мій пост"""

        # FIXME: перенести таблицю з постами в google sheet
        # TODO: додати ще колонку з інформацієї де саме знаходиться пост, це можна побачить біля інформатичного

        week_name: int = message.date.astimezone(self.kyiv_tz).weekday()

        # обробка події, якщо день відправлення - вихідний
        if week_name > 4:
            await message.answer(self.WEEKEND_PROMPT)
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        week_name: str = self.ukr_wn.get(str(week_name))
        teacher_name = await db.register.get_teacher_name(message.from_user.id)

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
