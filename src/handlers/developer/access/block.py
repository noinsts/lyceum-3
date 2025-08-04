from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.filters.callbacks import DeveloperBlockCallback, DeveloperBlockEnum
from src.states.developer import AccessBlock
from src.keyboards.inline import DeveloperBlockType, SubmitKeyboard
from src.validators import validate_teacher_name, validate_user_id
from src.db.connector import DBConnector

HANDLER_TRIGGER = "dev_access_block"
SUBMIT_TRIGGER = "submit_developer_access_block"
CANCEL_TRIGGER = "cancel_developer_access_block"


class BlockAccessHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == HANDLER_TRIGGER
        )

        self.router.callback_query.register(
            self.get_type,
            DeveloperBlockCallback.filter(),
            AccessBlock.waiting_for_type
        )

        self.router.message.register(
            self.get_user_id,
            F.text,
            AccessBlock.waiting_for_user_id
        )

        self.router.message.register(
            self.get_teacher_name,
            F.text,
            AccessBlock.waiting_for_teacher_name
        )

        self.router.callback_query.register(
            self.submit,
            F.data == SUBMIT_TRIGGER,
            AccessBlock.waiting_for_confirmation
        )

        self.router.callback_query.register(
            self.cancel,
            F.data == CANCEL_TRIGGER,
            AccessBlock.waiting_for_confirmation
        )

    @staticmethod
    async def handler(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(AccessBlock.waiting_for_type)

        await callback.message.answer(
            "Оберіть тип блокування",
            reply_markup=DeveloperBlockType().get_keyboard()
        )

        await callback.answer()

    @staticmethod
    async def get_type(callback: CallbackQuery, callback_data: DeveloperBlockCallback, state: FSMContext) -> None:
        value = callback_data.method

        match value:
            case DeveloperBlockEnum.BY_ID:
                response = "Добре, введіть <b>Telegram ID</b> для пошуку"
                fsm = AccessBlock.waiting_for_user_id
            case DeveloperBlockEnum.BY_TEACHER_NAME:
                response = "Добре, введіть <b>ім'я вчителя</b> для пошуку"
                fsm = AccessBlock.waiting_for_teacher_name
            case _:
                await callback.answer(
                    "❌ Помилка, куда ви нажмали...",
                    show_alert=True
                )
                return

        await state.set_state(fsm)

        await callback.message.edit_text(response, parse_mode=ParseMode.HTML)
        await callback.answer()

    async def get_user_id(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        user_id = message.text

        validate, reason = validate_user_id(user_id)

        if not validate:
            await message.answer(reason)
            return

        teacher_name = await db.verification.get_teacher_name(user_id)

        if not teacher_name:
            await message.answer("❌ В БД немає зареєстрованого user id")
            return

        await state.update_data(user_id=user_id)
        await state.update_data(teacher_name=teacher_name)

        await state.set_state(AccessBlock.waiting_for_confirmation)
        await self._send_feedback(message, state)

    async def get_teacher_name(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        teacher_name = message.text

        validate, reason = await validate_teacher_name(teacher_name, db)

        if not validate:
            await message.answer(reason)
            return

        user_id = await db.verification.get_user_id(teacher_name)

        if not user_id:
            await message.answer("❌ Цей вчитель не верифікований.")
            return

        await state.update_data(user_id=user_id)
        await state.update_data(teacher_name=teacher_name)

        await state.set_state(AccessBlock.waiting_for_confirmation)
        await self._send_feedback(message, state)

    @staticmethod
    async def _send_feedback(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        user_id = data.get("user_id")
        teacher_name = data.get("teacher_name")

        await message.answer(
            "<b>Ви хочете заблокувати доступ</b>:\n\n"
            f"🆔: <code>{user_id}</code>\n"
            f"🧑🏻‍🏫: <code>{teacher_name}</code>\n\n"
            f"<i>Оберіть наступну дію</i>",
            reply_markup=SubmitKeyboard().get_keyboard(SUBMIT_TRIGGER, CANCEL_TRIGGER),
            parse_mode=ParseMode.HTML
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()
        user_id = data.get("user_id")
        teacher_name = data.get("teacher_name")

        if not user_id or not teacher_name:
            await callback.message.edit_text("❌ Помилка: відсутні дані користувача")
            await callback.answer()
            return

        is_verif = await db.verification.is_verif(user_id, teacher_name)

        if not is_verif:
            await callback.message.edit_text("⚠️ Користувач вже заблокований")
            await state.clear()
            await callback.answer()
            return

        try:
            await db.verification.block_access(user_id)
            await callback.message.edit_text("✅ Доступ заблоковано")

        except Exception as e:
            await callback.message.edit_text(
                "❌ <b>Помилка при збереженні</b>\n\n"
                "Спробуйте пізніше або зверніться до адміністратора.",
                parse_mode=ParseMode.HTML
            )
            self.log.error(f"Error in block access for user {user_id}: {e}", exc_info=True)

        finally:
            await state.clear()
            await callback.answer()

    async def cancel(self, callback: CallbackQuery, state: FSMContext) -> None:
        await self.handler(callback, state)
