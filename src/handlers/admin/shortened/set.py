from enum import Enum
import datetime
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.states.admin.shortened import SetStates
from src.keyboards.inline import BackButton, BooleanKeyboard, SubmitKeyboard
from src.filters.callbacks import BooleanCallback
from src.decorators import next_state, with_validation
from src.validators import validate_date
from src.db.connector import DBConnector
from src.db.schemas import DaySchema


class Triggers(str, Enum):
    HUB = "admin_shortened_hub"
    HANDLER = "admin_shortened_set"
    SHOW_DATE = "admin_shortened_set_show_date"
    SHOW_STATUS = "admin_shortened_set_show_status"
    SHOW_SCHEDULE = "admin_shortened_set_show_schedule"
    SUBMIT = "admin_shortened_set_submit"


@dataclass(frozen=True)
class Messages:
    ENTER_A_DATE: str = (
        "Введіть дату в форматі 20-05-2011"
    )

    SELECT_STATUS: str = (
        "Оберіть статус"
    )

    ENTER_A_SCHEDULE: str = (
        "<b>Введіть розклад уроків</b>.\n\n"
        "Натисніть на розклад знизу - він скопіюється. "
        "Вставте його та модернізуйте\n\n"
        "<code>"
        "07:35 - 08:20 - Урок 0\n"
        "08:30 - 09:15 - Урок 1\n"
        "09:25 - 10:10 - Урок 2\n"
        "10:20 - 11:05 - Урок 3\n"
        "11:25 - 12:10 - Урок 4\n"
        "12:30 - 13:15 - Урок 5\n"
        "13:25 - 14:10 - Урок 6\n"
        "14:20 - 15:05 - Урок 7\n"
        "15:15 - 16:00 - Урок 8\n"
        "16:10 - 16:55 - Урок 9"
        "</code>"
    )

    CONFIRMATION: str = (
        "<b>Ви хочете встановити такі значення для {date}</b>\n\n"
        "Скорочення уроків: {status}\n\n"
        "Рокзад дзвінків:\n"
        "{schedule}\n\n"
        "<i>оберіть наступну дію</i>"
    )

    SUBMIT: str = (
        "✅ Успіх! Властивості дня встановлені"
    )


class SetHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.callback_query.register(
            self.show_date,
            F.data == Triggers.SHOW_DATE
        )

        self.router.message.register(
            self.get_date,
            SetStates.waiting_for_date
        )

        self.router.callback_query.register(
            self.show_status,
            F.data == Triggers.SHOW_STATUS
        )

        self.router.callback_query.register(
            self.get_status,
            BooleanCallback.filter(),
            SetStates.waiting_for_status
        )

        self.router.callback_query.register(
            self.show_schedule,
            F.data == Triggers.SHOW_SCHEDULE
        )

        self.router.message.register(
            self.get_schedule,
            SetStates.waiting_for_schedule
        )

        self.router.callback_query.register(
            self.submit,
            F.data == Triggers.SUBMIT,
            SetStates.waiting_for_confirmation
        )

    async def handler(self, callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await self.show_date(callback, state)

    # =========================
    # Форма
    # =========================

    @next_state(SetStates.waiting_for_date)
    async def show_date(self, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.ENTER_A_DATE,
            reply_markup=BackButton().get_keyboard(Triggers.HUB)
        )

    @with_validation(validate_date)
    async def get_date(self, message: Message, state: FSMContext) -> None:
        await state.update_data(date=message.text)
        await self.show_status(message, state)

    @next_state(SetStates.waiting_for_status)
    async def show_status(self, event: Message | CallbackQuery, state: FSMContext) -> None:
        kwargs = {
            "text": Messages.SELECT_STATUS,
            "reply_markup": BooleanKeyboard().get_keyboard(Triggers.SHOW_DATE)
        }

        await self._send_prompt(event, **kwargs)

    async def get_status(self, callback: CallbackQuery, state: FSMContext, callback_data: BooleanCallback) -> None:
        await state.update_data(status=callback_data.boolean)
        await self.show_schedule(callback, state)

    @next_state(SetStates.waiting_for_schedule)
    async def show_schedule(self, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.ENTER_A_SCHEDULE,
            parse_mode=ParseMode.HTML,
            reply_markup=BackButton().get_keyboard(Triggers.SHOW_STATUS)
        )

    async def get_schedule(self, message: Message, state: FSMContext) -> None:
        await state.update_data(schedule=message.text)
        await self.show_confirmation(message, state)

    # =========================
    # Підтвердження
    # =========================

    @next_state(SetStates.waiting_for_confirmation)
    async def show_confirmation(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()

        prompt = Messages.CONFIRMATION.format(
            date=data.get("date"),
            status="Так" if data.get("status") else "Ні",
            schedule=data.get("schedule")
        )

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.HUB)
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()

        try:
            date = data.get("date")
            date_obj = datetime.datetime.strptime(date, '%d-%m-%Y').date()

            obj = DaySchema(
                is_shortened=bool(data.get("status", False)),
                call_schedule=data.get("schedule"),
                date=date_obj
            )

            await db.day.set_day(obj)

            await callback.message.edit_text(
                Messages.SUBMIT,
                reply_markup=BackButton().get_keyboard(Triggers.HUB)
            )

            await state.clear()

        except Exception as e:
            self.log.error(f"Помилка під час встановлення властивостей дня: {e}", show_exc=True)

    # =========================
    # Приватні методи
    # =========================

    @staticmethod
    async def _send_prompt(event: Message | CallbackQuery, **kwargs) -> None:
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(**kwargs)
        elif isinstance(event, Message):
            await event.answer(**kwargs)
