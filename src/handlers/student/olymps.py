from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types import Message

from db.connector import DBConnector
from ..base import BaseHandler


class OlympHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == '🤓 Олімпіади'
        )

    @staticmethod
    async def handler(message: Message, db: DBConnector) -> None:
        form = await db.register.get_form(message.from_user.id)

        if not form:
            await message.answer(
                "❌ Не знайдено вашого класу в базі.\n"
                "Спробуйте пройти реєстрацію через команду /register"
            )
            return

        student_name = await db.register.get_student_name(message.from_user.id)

        if not student_name:
            await message.answer(
                "❌ Не знайдено вашого імені в базі.\n"
                "Спробуйте пройти реєстрацію через команду /register"
            )
            return

        olympiads = await db.olymp.my_olymps(student_name, form)

        if not olympiads:
            await message.answer("🎉 Вам пощастило! Вас ще не записали ні на жодну олімпіаду.")
            return

        for olymp in olympiads:
            prompt = (
                f"<b>🏅 Олімпіада з {olymp.subject}</b>\n"
                f"👩‍🏫 Вчитель: <i>{olymp.teacher_name}</i>\n"
                f"📍 Етап: <i>{olymp.stage_olymp}</i>\n"
                f"📅 Дата: <i>{olymp.date.strftime('%d.%m.%Y')}</i>\n"
                f"{f'📝 Примітка: <i>{olymp.note}</i>' if olymp.note else ''}"
            )

            await message.answer(prompt, parse_mode=ParseMode.HTML)
