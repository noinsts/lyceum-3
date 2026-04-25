from abc import ABC, abstractmethod
from typing import Type

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.filters.callbacks import DeveloperSearchCallback, DeveloperSearchEnum
from src.keyboards.inline import DeveloperSearchType, SubmitKeyboard
from src.validators import validate_teacher_name, validate_user_id
from src.db.connector import DBConnector
from src.states.developer import AccessBlock, AccessUnblock
from src.exceptions import ValidationError


class BaseBlockerAccessHandler(BaseHandler, ABC):
    def __init__(self):
        self.handler_trigger = self.get_handler_trigger()
        self.submit_trigger = self.get_submit_trigger()
        self.cancel_trigger = self.get_cancel_trigger()
        self.state = self.get_curr_state()

        super().__init__()

    @abstractmethod
    def get_curr_state(self) -> Type[AccessBlock | AccessUnblock]:
        """Повертає потрібний клас FSM"""
        pass

    @abstractmethod
    def get_handler_trigger(self) -> str:
        """Тригер для основного хендеру"""
        pass

    @abstractmethod
    def get_submit_trigger(self) -> str:
        """Тригер для підтвердення"""
        pass

    @abstractmethod
    def get_cancel_trigger(self) -> str:
        """Тригер для скасування"""
        pass

    @abstractmethod
    def get_action_name(self) -> str:
        """Назва дії (блокування/розблокувати)"""
        pass

    @abstractmethod
    def get_success_message(self) -> str:
        """Повідомлення про успіх"""
        pass

    @abstractmethod
    def get_already_processed_message(self) -> str:
        """Повідомлення коли дія вже виконанна"""
        pass

    @abstractmethod
    async def get_check_can_process(self, user_id: int, teacher_name: str, db: DBConnector) -> bool:
        """Перевіряє чи можна виконати дію"""
        pass

    @abstractmethod
    def is_verified(self) -> bool:
        """Логічне значення верифікації"""
        pass

    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == self.handler_trigger
        )

        self.router.callback_query.register(
            self.get_type,
            DeveloperSearchCallback.filter(),
            self.state.waiting_for_type
        )

        self.router.message.register(
            self.get_user_id,
            F.text,
            self.state.waiting_for_user_id
        )

        self.router.message.register(
            self.get_teacher_name,
            F.text,
            self.state.waiting_for_teacher_name
        )

        self.router.callback_query.register(
            self.submit,
            F.data == self.submit_trigger,
            self.state.waiting_for_confirmation
        )

        self.router.callback_query.register(
            self.cancel,
            F.data == self.submit_trigger,
            self.state.waiting_for_confirmation
        )

    async def handler(self, callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(self.state.waiting_for_type)

        await callback.message.answer(
            f"Оберіть тип {self.get_action_name()}",
            reply_markup=DeveloperSearchType().get_keyboard()
        )

        await callback.answer()

    async def get_type(self, callback: CallbackQuery, callback_data: DeveloperSearchCallback, state: FSMContext) -> None:
        value = callback_data.method

        match value:
            case DeveloperSearchEnum.BY_ID:
                response = "Добре, введіть <b>Telegram ID</b> для пошуку"
                fsm = self.state.waiting_for_user_id
            case DeveloperSearchEnum.BY_TEACHER_NAME:
                response = "Добре, введіть <b>ім'я вчителя</b> для пошуку"
                fsm = self.state.waiting_for_teacher_name
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

        try:
            validate_user_id(user_id)
        except ValidationError as e:
            await message.answer(str(e))
            return

        teacher_name = await db.verification.get_teacher_name(int(user_id))

        if not teacher_name:
            await message.answer("❌ В БД немає зареєстрованого user id")
            return

        await state.update_data(user_id=int(user_id))
        await state.update_data(teacher_name=teacher_name)

        await state.set_state(self.state.waiting_for_confirmation)
        await self._send_feedback(message, state)

    async def get_teacher_name(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        teacher_name = message.text

        try:
            await validate_teacher_name(teacher_name)
        except ValidationError as e:
            await message.answer(str(e))
            return

        user_id = await db.verification.get_user_id(teacher_name)

        if not user_id:
            await message.answer("❌ Цей вчитель не верифікований.")
            return

        await state.update_data(user_id=user_id)
        await state.update_data(teacher_name=teacher_name)

        await state.set_state(self.state.waiting_for_confirmation)
        await self._send_feedback(message, state)

    async def _send_feedback(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        user_id = data.get("user_id")
        teacher_name = data.get("teacher_name")

        await message.answer(
            f"<b>Ви хочете {self.get_action_name()} доступ</b>:\n\n"
            f"🆔: <code>{user_id}</code>\n"
            f"🧑🏻‍🏫: <code>{teacher_name}</code>\n\n"
            f"<i>Оберіть наступну дію</i>",
            reply_markup=SubmitKeyboard().get_keyboard(self.submit_trigger, self.cancel_trigger),
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

        is_verif = await self.get_check_can_process(user_id, teacher_name, db)

        if not is_verif:
            await callback.message.edit_text(self.get_already_processed_message())
            await state.clear()
            await callback.answer()
            return

        try:
            await db.verification.set_access(user_id, self.is_verified())
            await callback.message.edit_text(self.get_success_message())

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
