from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from ...base import BaseHandler
from src.keyboards.inline import DeveloperSearchType
from src.filters.callbacks import DeveloperSearchCallback, DeveloperSearchEnum
from src.states.developer import AccessStatus
from src.db.connector import DBConnector
from src.validators import validate_user_id, validate_teacher_name

HANDLER_TRIGGER = "dev_access_status"
DB_EXCEPTION_RESPONSE = "❌ Помилка. В БД немає інформації про верифікацію."
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
            F.data == HANDLER_TRIGGER
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

    @staticmethod
    async def handler(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AccessStatus.waiting_for_type)

        await callback.message.answer(
            "Вкажіть тип пошуку",
            reply_markup=DeveloperSearchType().get_keyboard()
        )
        await callback.answer()

    @staticmethod
    async def get_type(callback: CallbackQuery, callback_data: DeveloperSearchCallback, state: FSMContext) -> None:
        value = callback_data.method
        search_data = SEARCH_OPTIONS.get(value)

        if not search_data:
            await callback.answer("❌ Помилка, куда ви нажмали...", show_alert=True)
            return

        await state.set_state(search_data["fsm"])

        await callback.message.edit_text(search_data["response"], parse_mode=ParseMode.HTML)
        await callback.answer()

    async def get_user_id(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        user_id = message.text

        validate, reason = validate_user_id(user_id)

        if not validate:
            await message.answer(reason)
            return

        user_id = int(user_id)

        teacher_name = await db.verification.get_teacher_name(user_id)

        if not teacher_name:
            await message.answer(DB_EXCEPTION_RESPONSE)
            return

        await state.update_data(user_id=user_id, teacher_name=teacher_name)
        await self.continue_search_flow(message, state, db)

    async def get_teacher_name(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        teacher_name = message.text

        validate, reason = await validate_teacher_name(teacher_name, db)

        if not validate:
            await message.answer(reason)
            return

        user_id = await db.verification.get_user_id(teacher_name)

        if not user_id:
            await message.answer(DB_EXCEPTION_RESPONSE)
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
            await message.answer(DB_EXCEPTION_RESPONSE)
            return

        status = "Верифіковано" if verif else "Заблоковано"

        response = USER_INFO_TEMPLATE.format(
            user_id=user_id,
            teacher_name=teacher_name,
            status=status
        )

        await message.answer(response, parse_mode=ParseMode.HTML)
        await state.clear()
