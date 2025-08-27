from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.db.connector import DBConnector
from src.db.schemas import AddUserSchema
from src.utils import classes, parse_hub_keyboard
from src.states import RegisterStates
from src.keyboards.inline import UserTypeKeyboard, SelectForm
from src.filters.callbacks import UserTypeCallback, FormsListCallback
from src.enums import DBUserType
from src.validators import validate_student_name, validate_teacher_name
from src.decorators import next_state, with_validation
from src.exceptions import ValidationError


class Triggers(str, Enum):
    COMMAND = "register"
    CALLBACK = "register_start"


@dataclass(frozen=True)
class Messages:
    SELECT_A_TYPE: str = (
        "Хто ви? Оберіть нижче 👇"
    )

    SELECT_FORM: str = (
        "Зі списку нижче оберіть ваш клас"
    )

    ENTER_A_TEACHER_NAME: str = (
        "Будь ласка, вкажіть ваше ПІП (повністю)"
    )

    NO_FORM_FOUND: str = (
        "Такого класу в нас немає. Може, перевірите ще раз? 🤔"
    )

    ENTER_A_STUDENT_NAME: str = (
        "Добре, тепер введіть ваше прізвище та ім'я, наприклад: Лепський Артем"
    )

    SUCCESS_TITLE: str = (
        "✅ <b>Успіх! Дані успішно записані!</b>\n\n"
    )

    CORRECT_HINT: str = (
        "\n❓ <i>Зробили одрук? Скористайтесь командою /register для повторної реєстрації</i>"
    )

    REGISTER_ERROR: str = (
        "❌ Помилка під час реєстрації, спробуйте знову"
    )

    UNKNOWN_USER_TYPE: str = (
        "❌ Помилка: невідомий тип користувача"
    )


class RegisterHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.start_register,
            Command(Triggers.COMMAND)
        )

        self.router.callback_query.register(
            self.start_register,
            F.data == Triggers.CALLBACK
        )

        self.router.callback_query.register(
            self.get_user_type,
            UserTypeCallback.filter(),
            RegisterStates.waiting_for_type
        )

        self.router.callback_query.register(
            self.get_form,
            FormsListCallback.filter(),
            RegisterStates.waiting_for_form
        )

        self.router.message.register(
            self.get_teacher_name,
            RegisterStates.waiting_for_teacher_name
        )

        self.router.message.register(
            self.get_student_name,
            RegisterStates.waiting_for_student_name
        )

        self.router.message.register(
            self.finally_register,
            RegisterStates.finally_register
        )

    # =================================
    # Форма
    # =================================

    @classmethod
    @next_state(RegisterStates.waiting_for_type)
    async def start_register(cls, event: Message | CallbackQuery, state: FSMContext) -> None:
        """Запускає процес реєстрації: питає тип користувача (учень/вчитель)"""
        kwargs = {
            "text": Messages.SELECT_A_TYPE,
            "reply_markup": UserTypeKeyboard().get_keyboard()
        }

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(**kwargs)
        elif isinstance(event, Message):
            await event.answer(**kwargs)

    @classmethod
    async def get_user_type(cls, callback: CallbackQuery, state: FSMContext, callback_data: UserTypeCallback) -> None:
        """Отримання типу користувача (учень/вчитель)"""

        try:
            utype = DBUserType[callback_data.utype]
        except Exception:
            await callback.answer(Messages.UNKNOWN_USER_TYPE, show_alert=True)
            return

        await state.update_data(user_type=utype)

        match utype:
            case DBUserType.STUDENT:
                kwargs = {
                    "text": Messages.SELECT_FORM,
                    "reply_markup": SelectForm().get_keyboard(classes.CLASSES, False, Triggers.CALLBACK)
                }
                fsm = RegisterStates.waiting_for_form
            case DBUserType.TEACHER:
                kwargs = {
                    "text": Messages.ENTER_A_TEACHER_NAME
                }
                fsm = RegisterStates.waiting_for_teacher_name

        await callback.message.edit_text(**kwargs)
        await state.set_state(fsm)

    @next_state(RegisterStates.waiting_for_student_name)
    async def get_form(self, callback: CallbackQuery, state: FSMContext, callback_data: FormsListCallback) -> None:
        """Отримання класу учня"""
        await state.update_data(form=callback_data.form)
        await callback.message.edit_text(Messages.ENTER_A_STUDENT_NAME)

    @with_validation(validate_student_name)
    @next_state(RegisterStates.finally_register)
    async def get_student_name(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        """Отримання імені учня від користувача"""
        await state.update_data(student_name=message.text)
        await self.finally_register(message, state, db)

    @next_state(RegisterStates.finally_register)
    async def get_teacher_name(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        """Отримання імені вчителя від користувача"""
        teacher_name = message.text.strip()

        try:
            await validate_teacher_name(teacher_name, db)
        except ValidationError as e:
            await message.answer(str(e))
            return

        await state.update_data(teacher_name=teacher_name)
        await self.finally_register(message, state, db)

    # =================================
    # Реєстрація
    # =================================

    async def finally_register(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        """Фінал реєстрації: запис у базу, показ підтвердження та меню користувача"""
        data = await state.get_data()

        try:
            await self._save_to_db(message, db, data)
            success_message = await self._build_success_message(message, data, db)

            await message.answer(
                success_message,
                reply_markup=await parse_hub_keyboard(message.from_user.id),
                parse_mode=ParseMode.HTML
            )

            await state.clear()
        except Exception as e:
            self.log.error(f"Помилка під час реєстрації користувача: {e}", exc_info=True)
            await message.answer(Messages.REGISTER_ERROR)

    @staticmethod
    async def _save_to_db(message: Message, db: DBConnector, data: Dict[str, Any]):
        """Зберігає користувача в базу даних"""
        user_type = data.get("user_type")

        if isinstance(user_type, DBUserType):
            user_type_value = user_type.value
        elif isinstance(user_type, str):
            user_type_value = user_type
        else:
            raise ValueError(f"Невідомий тип user_type: {type(user_type)}")

        await db.register.add_user(
            AddUserSchema(
                user_id=int(message.from_user.id),
                full_name=message.from_user.full_name,
                username=message.from_user.username,
                user_type=user_type_value,
                form=data.get("form"),
                teacher_name=data.get("teacher_name"),
                student_name=data.get("student_name")
            )
        )

    async def _build_success_message(self, message: Message, data: Dict[str, Any], db: DBConnector) -> str:
        user_type = data.get("user_type")

        msg = Messages.SUCCESS_TITLE
        msg += f"<b>Тип</b>: {self._get_user_type_pretty(user_type)}\n"

        if user_type == DBUserType.STUDENT:
            msg += await self._build_student_info(db, data)
        elif user_type == DBUserType.TEACHER:
            msg += await self._build_teacher_info(message, db, data)

        msg += Messages.CORRECT_HINT

        return msg

    @staticmethod
    def _get_user_type_pretty(user_type: str) -> DBUserType:
        """Повертає читабельну назву типу користувача"""
        user_type_mapping = {
            DBUserType.STUDENT: "Учень",
            DBUserType.TEACHER: "Вчитель"
        }
        return user_type_mapping.get(user_type)

    @staticmethod
    async def _build_student_info(db: DBConnector, data: Dict[str, Any]) -> str:
        """Будує детальну інформацію про учня"""
        try:
            form_info = await db.form.get_info(data.get("form"))
            depth_subject = form_info.depth_subject
            depth_subject_display = depth_subject.value
            form_teacher_id = form_info.teacher_id
            form_teacher_name = await db.verification.get_teacher_name_by_id(form_teacher_id)
        except Exception:
            depth_subject_display = None
            form_teacher_name = None

        return (
            f"<b>Ім'я</b>: {data.get("student_name", "не встановлено")}\n"
            f"<b>Клас</b>: {data.get("form", "не встановлено")}\n"
            f"<b>Профіль класу</b>: {depth_subject_display or "не встановлено"}\n"
            f"<b>Класний керівник</b>: {form_teacher_name or "не встановлено"}\n"
        )

    @staticmethod
    async def _build_teacher_info(message: Message, db: DBConnector, data: Dict[str, Any]) -> str:
        """Будує детальну інформацію про вчителя"""
        teacher_name = data.get("teacher_name")

        if not teacher_name:
            return "<b>ПІП</b>: не встановлено"

        try:
            teacher_id = await db.verification.get_teacher_id(teacher_name)
            form = await db.form.get_form_by_teacher(teacher_id) if teacher_id else None
            is_verified = await db.verification.is_verif(message.from_user.id, teacher_name)
        except Exception:
            form = None
            is_verified = None

        return (
            f"<b>ПІП:</b> {data.get("teacher_name")}\n"
            f"<b>Класний керівник:</b> {form or "не встановлено"}\n"
            f"<b>Статус верифікації:</b> {"✅" if is_verified else "❌"}\n"
        )

        # TODO: якщо статус верифікація - False, то додать inline кнопку про верифікацію
