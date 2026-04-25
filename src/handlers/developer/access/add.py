from typing import Optional, Tuple, List

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from src.db.connector import DBConnector
from ...base import BaseHandler
from src.states import DevAddAccess
from src.keyboards.inline import SubmitKeyboard
from src.validators import validate_user_id, validate_teacher_name
from src.exceptions import ValidationError
from src.service import broadcast


class Triggers:
    """Константи для тригерів callback"""
    HANDLER = "dev_access_add"
    SUBMIT = "add_access_submit"
    CANCEL = "add_access_cancel"


class Messages:
    """Константи повідомлень"""
    INITIAL_PROMPT = (
        "<b>📝 Додавання доступу</b>\n\n"
        "Введіть дані у такому форматі:\n\n"
        "<code>12345678</code>\n"
        "<code>teacher_name</code>\n\n"
        "<i>Де перший рядок - user_id (тільки цифри), "
        "другий рядок - ім'я вчителя</i>"
    )

    VALIDATION_ERRORS = {
        "empty_data": "⚠️ Будь ласка, введіть текстові дані",
        "insufficient_data": "⚠️ Очікується більше інформації (user_id та teacher_name)",
        "too_many_lines": "⚠️ Забагато рядків. Введіть тільки user_id та teacher_name"
    }

    ATTENTION = (
        "<b>⚠️ Попередження</b>\n\n"
        "Акаунт з <code>user_id = {user_id}</code> вже існує.\n"
        "Ім'я вчителя буде <b>оновлено</b> з "
        "<code>{existing}</code> на <code>{teacher_name}</code>.\n\n"
        "<i>Продовжити?</i>"
    )

    CONFIRMATION = (
        "<b>Підтвердження даних</b>\n\n"
        "🆔: <code>{user_id}</code>\n"
        "🧑🏻‍🏫: <code>{teacher_name}</code>\n\n"
        "<i>Все правильно?</i>"
    )

    SAVE_ERROR = (
        "❌ <b>Помилка при збереженні<b>\n\n"
        "Спробуйте пізніше або зверніться до адміністратора."
    )

    DB_ERROR = (
        "❌ Помилка бази даних "
        "Спробуйте пізніше або зверніться до адміністратора."
    )

    SUCCESS = (
        "✅ <b>Успішно</b>\n\n"
        "Доступ для <code>{name}</code> "
        "(ID: <code>{user_id}</code>) додано до системи."
    )

    USER_MESSAGE: str = (
        "🎉 Вітаємо, вам назначено верифікацію."
    )

    CANCELED = (
        "🔄 <b>Скасовано.</b>\n\n"
        "Операція скасована."
    )


class AddAccessHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.message.register(
            self.collect_data,
            DevAddAccess.waiting_for_data
        )

        self.router.callback_query.register(
            self.submit,
            DevAddAccess.waiting_for_confirmation,
            F.data == Triggers.SUBMIT
        )

        self.router.callback_query.register(
            self.cancel,
            DevAddAccess.waiting_for_confirmation,
            F.data == Triggers.CANCEL
        )

    @staticmethod
    async def handler(callback: CallbackQuery, state: FSMContext) -> None:
        """Обробка стартового callback"""
        await callback.answer()
        await callback.message.answer(Messages.INITIAL_PROMPT, parse_mode=ParseMode.HTML)

        await state.set_state(DevAddAccess.waiting_for_data)

    async def collect_data(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        try:
            if not await self._validate_and_process_input(message, state, db):
                return

            await self._send_response(message, state, db)

        except Exception as e:
            await self._handler_db_error(message, state, e, "collect data")

    async def _validate_and_process_input(self, message: Message, state: FSMContext, db: DBConnector) -> bool:
        """Валідує введені дані"""
        validate, reason, lines = self._validate_data(message.text)

        if not validate:
            await message.answer(reason)
            return False

        user_id, tn = lines[0], lines[1]

        try:
            validate_user_id(user_id)
        except ValidationError as e:
            await message.answer(str(e))
            return False

        user_id = int(user_id)

        try:
            await validate_teacher_name(tn)
        except ValidationError as e:
            await message.answer(str(e))
            return False

        await state.update_data(user_id=user_id, teacher_name=tn)
        return True

    async def _send_response(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()
        user_id = data.get("user_id")
        teacher_name = data.get("teacher_name")

        existing_teacher = await db.verification.get_name(user_id)
        prompt = self._get_confirmation_prompt(user_id, teacher_name, existing_teacher)

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.CANCEL)
        )

        await state.set_state(DevAddAccess.waiting_for_confirmation)

    @staticmethod
    def _validate_data(raw: Optional[str]) -> Tuple[bool, Optional[str], Optional[List]]:
        """
        Валідує введені дані та перетворює в масив

        Args:
            raw (Optional[str]): текст, який потрібно відвалідувати

        Returns:
            Tuple:
                - bool: чи пройшов валідацію
                - Optional[str]: причина фейлу валідації
                - Optional[List]: оброблений масив
        """
        if not raw:
            return False, Messages.VALIDATION_ERRORS['empty_data'], None

        lines = [line.strip() for line in raw.split("\n") if line.strip()]

        # оброблюємо помилка
        if len(lines) < 2:
            return False, Messages.VALIDATION_ERRORS['insufficient_data'], None

        if len(lines) > 2:
            return False, Messages.VALIDATION_ERRORS['too_many_lines'], None

        return True, None, lines

    @staticmethod
    def _get_confirmation_prompt(user_id: int, teacher_name: str, existing: Optional[str]) -> str:
        """Повертає промпт підтвердження, що буде відправлено користувачу"""
        if existing:
            return Messages.ATTENTION.format(
                user_id=user_id,
                teacher_name=teacher_name,
                existing=existing
            )
        else:
            return Messages.CONFIRMATION.format(
                user_id=user_id,
                teacher_name=teacher_name
            )

    async def _handler_db_error(self, message: Message, state: FSMContext, e: Exception, context: str) -> None:
        """Оброблює помилки"""
        await message.answer(Messages.DB_ERROR, parse_mode=ParseMode.HTML)
        self.log.error(f"Помилка під час devmode/access/add: {context}: {e}")
        await state.clear()

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        """Обробка callback погодження"""
        try:
            data = await state.get_data()
            user_id = data.get("user_id")
            teacher_name = data.get("teacher_name")

            await db.verification.add_verif_teacher(user_id, teacher_name)

            response = Messages.SUCCESS.format(
                name=teacher_name,
                user_id=user_id
            )

            _, _ = await broadcast(Messages.USER_MESSAGE, [user_id])

            await callback.message.edit_text(response, parse_mode=ParseMode.HTML)
            await callback.answer()

        except Exception as e:
            await callback.answer(Messages.SAVE_ERROR, show_alert=True)
            self.log.error(f"Error devmode/access/add: saving: {e}")

        finally:
            await state.clear()

    @staticmethod
    async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
        """Обробка callback скасування операції"""
        await callback.answer()
        await state.clear()

        await callback.message.edit_text(Messages.CANCELED, parse_mode=ParseMode.HTML)
