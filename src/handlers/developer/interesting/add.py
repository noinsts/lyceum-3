import datetime
from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import BackButton, SubmitKeyboard
from src.states.developer.interesting import AddStates
from src.decorators import next_state, with_validation
from src.validators import validate_date
from src.db.connector import DBConnector


class Triggers(str, Enum):
    HUB = "dev_interesting_hub"
    HANDLER = "dev_interesting_add"
    SHOW_MESSAGE = "dev_interesting_add_show_message"
    SHOW_DATE = "dev_interesting_add_show_date"
    SUBMIT = "dev_interesting_add_submit"


@dataclass(frozen=True)
class Messages:
    ENTER_A_MESSAGE: str = (
        "Введіть промпт, який буде в цікавій кнопці"
    )

    ENTER_A_DATE: str = (
        "В який день буде відображатись це повідомлення? (формат: 20-05-2011)"
    )

    SUCCESS: str = (
        "✅ Супер! Текст встановлено"
    )


class AddHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.callback_query.register(
            self.show_prompt,
            F.data == Triggers.SHOW_MESSAGE
        )

        self.router.message.register(
            self.get_prompt,
            AddStates.waiting_for_message
        )

        self.router.callback_query.register(
            self.show_date,
            F.data == Triggers.SHOW_DATE
        )

        self.router.message.register(
            self.get_date,
            AddStates.waiting_for_date
        )

        self.router.callback_query.register(
            self.submit,
            F.data == Triggers.SUBMIT,
            AddStates.waiting_for_confirmation
        )

    async def handler(self, callback: CallbackQuery, state: FSMContext) -> None:
        await self.show_prompt(callback, state)

    # =========================
    # Форма
    # =========================

    @next_state(AddStates.waiting_for_message)
    async def show_prompt(self, event: Message | CallbackQuery, state: FSMContext) -> None:
        kwargs = {
            "text": Messages.ENTER_A_MESSAGE,
            "reply_markup": BackButton().get_keyboard(Triggers.HUB)
        }

        await self._send_message(event, **kwargs)

    async def get_prompt(self, message: Message, state: FSMContext) -> None:
        await state.update_data(prompt=message.text)
        await self.show_date(message, state)

    @next_state(AddStates.waiting_for_date)
    async def show_date(self, event: Message | CallbackQuery, state: FSMContext) -> None:
        kwargs = {
            "text": Messages.ENTER_A_DATE,
            "reply_markup": BackButton().get_keyboard(Triggers.SHOW_MESSAGE)
        }

        await self._send_message(event, **kwargs)

    @with_validation(validate_date)
    async def get_date(self, message: Message, state: FSMContext) -> None:
        await state.update_data(date=message.text)
        await self.show_confirmation(message, state)

    # =========================
    # Підтвердження
    # =========================

    @next_state(AddStates.waiting_for_confirmation)
    async def show_confirmation(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        msg = data.get("prompt")
        date = data.get("date")

        prompt = (
            f"<b>Ви хочете встановити наступний текст цікавої кнопки на {date}</b>\n\n"
            f"💌: {msg}"
        )

        await message.answer(
            prompt,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.HUB),
            parse_mode=ParseMode.HTML
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()

        try:
            prompt = data.get("prompt")
            date = data.get("date")
            date_obj = datetime.datetime.strptime(date, '%d-%m-%Y').date()

            await db.interesting.add_new(prompt, date_obj)

            await callback.message.edit_text(
                Messages.SUCCESS,
                reply_markup=BackButton().get_keyboard(Triggers.HUB)
            )

            await state.clear()

        except Exception as e:
            await callback.answer(f"Помилка: {e}", show_alert=True)
            self.log.info(f"Помилка під час встановлення тексту цікавої кнопки: {e}", exc_info=True)

    # =========================
    # Приватні методи
    # =========================

    @staticmethod
    async def _send_message(event: Message | CallbackQuery, **kwargs) -> None:
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(**kwargs)
        elif isinstance(event, Message):
            await event.answer(**kwargs)
