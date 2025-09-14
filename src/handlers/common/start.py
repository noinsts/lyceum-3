from typing import Dict, Any, Optional
from dataclasses import dataclass

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from src.db.connector import DBConnector
from src.enums import DBUserType
from src.handlers.base import BaseHandler
from src.keyboards.reply import HubMenu, HubTeacher
from src.handlers.common.register import RegisterHandler
from src.keyboards.inline import TelegramChannel
from src.handlers.admin.hub import AdminHubHandler
from src.handlers.developer.hub import DevHubHandler
from settings.admins import Admins
from settings.developers import Developers
from src.db.models import UserModel


@dataclass(frozen=True)
class Messages:
    STUDENT: str = (
        "👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
        "Ви зареєстровані як {student_name}, учень(-ця) <b>{form}</b> класу.\n\n"
        "Якщо хочете змінити дані, використайте команду /register"
    )

    TEACHER: str = (
        "👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
        "Ви зареєстровані як вчитель <b>{teacher_name}</b>\n"
        "Статус верифікації: <b>{is_verif}</b>\n"
        "Класний керівник: <b>{form}</b>\n\n"
        "Якщо хочете змінити дані, використайте команду /register"
    )

    UNREGISTERED_USER: str = (
        "👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
        "Будь-ласка, зареєструйтеся, щоб скористатись всіма можливостями бота\n\n"
    )


class StartHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.start_cmd, CommandStart())

    async def start_cmd(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        """Обробник команди start"""
        user_id = message.from_user.id

        await self._handle_special_users(message, state, user_id)

        user = await db.register.get_user(user_id)

        if user:
            await self._handle_registered_user(message, user, db)
        else:
            await self._handler_unregistered_user(message, state)

    @classmethod
    async def _handle_special_users(cls, message: Message, state: FSMContext, user_id: int) -> None:
        if user_id in Admins().ADMINS:
            await DevHubHandler().show_hub(message, state)

        if user_id in Developers().DEVELOPERS:
            await AdminHubHandler().show_hub(message, state)

    async def _handle_registered_user(self, message: Message, user: UserModel, db: DBConnector) -> None:
        match user.user_type:
            case DBUserType.STUDENT:
                kwargs = self._get_student_kwargs(user)
            case DBUserType.TEACHER:
                is_verif = await db.verification.is_verif(message.from_user.id, user.teacher_name)
                teacher_id = await db.verification.get_teacher_id(user.teacher_name)
                form = await db.form.get_form_by_teacher(teacher_id)
                kwargs = self._get_teacher_kwargs(user.teacher_name, is_verif, form)

        await message.answer(**kwargs)

    @classmethod
    def _get_student_kwargs(cls, user: UserModel) -> Dict[str, Any]:
        return {
            "text": Messages.STUDENT.format(
                form=user.form,
                student_name=user.student_name
            ),
            "reply_markup": HubMenu().get_keyboard(),
            "parse_mode": ParseMode.HTML
        }

    @classmethod
    def _get_teacher_kwargs(
            cls,
            teacher_name: str,
            is_verif: Optional[bool],
            form: Optional[str]
    ) -> Dict[str, Any]:
        return {
            "text": Messages.TEACHER.format(
                teacher_name=teacher_name,
                is_verif="✅" if is_verif else "❌",
                form=form or "не встановлено"
            ),
            "reply_markup": HubTeacher().get_keyboard(),
            "parse_mode": ParseMode.HTML
        }

    @classmethod
    async def _handler_unregistered_user(cls, message: Message, state: FSMContext) -> None:
        await message.answer(
            Messages.UNREGISTERED_USER,
            reply_markup=TelegramChannel().get_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await RegisterHandler().start_register(message, state)
