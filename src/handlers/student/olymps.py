from typing import Optional

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types import Message

from ..base import BaseHandler
from db.connector import DBConnector
from src.exceptions import ValidationError


class Triggers:
    HANDLER = "🤓 Олімпіади"


class Messages:
    NO_OLYMPIAD = (
        "🎉 Вам пощастило! Вас ще не записали ні на жодну олімпіаду."
    )

    OLYMPIAD = (
        "<b>🏅 Олімпіада з {subject}</b>\n"
        "👩‍🏫 Вчитель: <i>{teacher_name}</i>\n"
        "📍 Етап: <i>{stage_olymp}</i>\n"
        "📅 Дата: <i>{date}</i>\n"
        "📝 Примітка: <i>{note}</i>"
    )

    VALIDATION_ERRORS = {
        "no_student_name": "❌ Не знайдено вашого імені в базі.\nСпробуйте пройти реєстрацію через команду /register",
        "no_form": "❌ Не знайдено вашого класу в базі.\nСпробуйте пройти реєстрацію через команду /register"
    }


class OlympHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == Triggers.HANDLER
        )

    async def handler(self, message: Message, db: DBConnector) -> None:
        form = await db.register.get_form(message.from_user.id)
        student_name = await db.register.get_student_name(message.from_user.id)

        try:
            self._validate(student_name, form)
        except ValidationError as e:
            await message.answer(str(e))
            return

        olympiads = await db.olymp.my_olymps(student_name, form)

        if not olympiads:
            await message.answer(Messages.NO_OLYMPIAD)
            return

        for olymp in olympiads:
            prompt = Messages.OLYMPIAD.format(
                subject=olymp.subject,
                teacher_name=olymp.teacher_name,
                stage_olymp=olymp.stage_olymp,
                date=olymp.date.strftime('%d.%m.%Y'),
                note=olymp.note or '(Відсутня)'
            )

            await message.answer(prompt, parse_mode=ParseMode.HTML)

    @staticmethod
    def _validate(student_name: Optional[str], form: Optional[str]) -> bool:
        """
        Метод валідації

        Args:
            student_name (str): ім'я студента
            form (str): назва класу

        Returns:
            bool: чи пройшла верифікація

        Raises:
            ValidationError: якщо валідація не пройдена
        """
        if not student_name:
            raise ValidationError(Messages.VALIDATION_ERRORS["no_student_name"])

        if not form:
            raise ValidationError(Messages.VALIDATION_ERRORS["no_form"])

        return True
