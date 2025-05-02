from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types import Message

from .base import BaseHandler

class TeacherHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.WEEKEND_PROMPT = "Сьогодні вихідний! Чому ви думаєте про роботу? Може краще відпочити 🙂‍↕️"
        self.WEEEKEND_STICKER = "CAACAgIAAxkBAAEOZ1doFUn9Y0TR-qURiQeEb7HZdGC2qQACOjMAAlG5gEjH0Q7wxWFwrDYE"
        self.HAPPY_GUY = "CAACAgIAAxkBAAEOZ1loFUxiV3fJxTbJ0Q6iD6LDAkhsxwACBTgAAp17sEknYmmEwwt6pTYE"


    def register_handler(self) -> None:
        self.router.message.register(self.my_post, F.text == '🚦 Мій пост')


    async def my_post(self, message: Message) -> None:
        """Обробник кнопки 🚦 Мій пост"""
        self.db.register.update_udata(message.from_user)  # оновлення даних про ім'я користувача та нікнейм

        week_name: int = message.date.astimezone(self.kyiv_tz).weekday()

        # обробка події, якщо день відправлення - вихідний
        if week_name > 4:
            await message.answer(self.WEEKEND_PROMPT)
            await message.answer_sticker(self.WEEEKEND_STICKER)
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
