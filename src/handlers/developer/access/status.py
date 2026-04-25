from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from ...base import BaseHandler
from src.keyboards.inline import DeveloperSearchType, BackButton
from src.filters.callbacks import DeveloperSearchCallback, DeveloperSearchEnum
from src.states.developer import AccessStatus
from src.db.connector import DBConnector
from src.validators import validate_user_id, validate_teacher_name
from src.exceptions import ValidationError
from src.decorators import next_state


class Triggers:
    HUB = "dev_access_hub"
    HANDLER = "dev_access_status"


class Messages:
    HANDLER = (
        "Вкажіть тип пошуку"
    )

    ERROR = (
        "❌ Помилка, куда ви нажмали..."
    )

    DB_EXCEPTION = (
        "❌ Помилка. В БД немає інформації про верифікацію."
    )

    USER_INFO_TEMPLATE = (
        "<b>Інформація про користувача.</b>\n\n"
        "🆔: <code>{user_id}</code>\n"
        "🧑🏻‍🏫: <code>{teacher_name}</code>\n"
        "🔐: <code>{status}</code>"
    )

    SEARCH_OPTIONS = {
        DeveloperSearchEnum.BY_ID: {
            "response": "Добре, введіть <b>Telegram ID</b> для пошуку",
            "fsm": AccessStatus.waiting_for_user_id
        },
        DeveloperSearchEnum.BY_TEACHER_NAME: {
            "response": "Добре, введіть <b>ім'я вчителя</b> для пошуку",
            "fsm": AccessStatus.waiting_for_teacher_name
        }
    }


class StatusAccessHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.callback_query.register(
            self.get_type,
            DeveloperSearchCallback.filter(),
            AccessStatus.waiting_for_type
        )

        self.router.message.register(
            self.get_user_id,
            AccessStatus.waiting_for_user_id
        )

        self.router.message.register(
            self.get_teacher_name,
            AccessStatus.waiting_for_teacher_name
        )

    @classmethod
    @next_state(AccessStatus.waiting_for_type)
    async def handler(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.HANDLER,
            reply_markup=DeveloperSearchType().get_keyboard(Triggers.HUB)
        )

    @staticmethod
    async def get_type(callback: CallbackQuery, callback_data: DeveloperSearchCallback, state: FSMContext) -> None:
        value = callback_data.method
        search_data = Messages.SEARCH_OPTIONS.get(value)

        if not search_data:
            await callback.answer(Messages.ERROR, show_alert=True)
            return

        await state.set_state(search_data["fsm"])

        await callback.message.edit_text(search_data["response"], parse_mode=ParseMode.HTML)
        await callback.answer()

    async def get_user_id(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        user_id = message.text

        try:
            validate_user_id(user_id)
        except ValidationError as e:
            await message.answer(str(e))
            return

        user_id = int(user_id)

        teacher_name = await db.verification.get_teacher_name(user_id)

        if not teacher_name:
            await message.answer(Messages.DB_EXCEPTION)
            return

        await state.update_data(user_id=user_id, teacher_name=teacher_name)
        await self.continue_search_flow(message, state, db)

    async def get_teacher_name(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        teacher_name = message.text

        try:
            await validate_teacher_name(teacher_name)
        except ValidationError as e:
            await message.answer(str(e))
            return

        user_id = await db.verification.get_user_id(teacher_name)

        if not user_id:
            await message.answer(Messages.DB_EXCEPTION)
            return

        await state.update_data(user_id=user_id, teacher_name=teacher_name)
        await self.continue_search_flow(message, state, db)

    @staticmethod
    async def continue_search_flow(message: Message, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()

        user_id = data.get("user_id")
        teacher_name = data.get("teacher_name")

        verif = await db.verification.is_verif(user_id, teacher_name)

        if verif is None:
            await message.answer(Messages.DB_EXCEPTION)
            return

        status = "Верифіковано" if verif else "Заблоковано"

        response = Messages.USER_INFO_TEMPLATE.format(
            user_id=user_id,
            teacher_name=teacher_name,
            status=status
        )

        await message.answer(
            response,
            parse_mode=ParseMode.HTML,
            reply_markup=BackButton().get_keyboard(Triggers.HUB)
        )
        await state.clear()
