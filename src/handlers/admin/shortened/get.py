from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.states.admin.shortened import GetStates
from src.decorators import next_state, with_validation
from src.db.connector import DBConnector
from src.validators import validate_date
from src.keyboards.inline import BackButton


class Triggers(str, Enum):
    HUB = "admin_shortened_hub"
    HANDLER = "admin_shortened_get"


@dataclass(frozen=True)
class Messages:
    HANDLER: str = (
        "Введіть день в форматі 20-05-2011"
    )

    NO_INFO: str = (
        "❌ Інформації за <b>{day}</b> не знайдено."
    )

    INFO: str = (
        "📅 <b>Інформація про {day}</b>\n\n"
        "⏱ <b>Скорочені уроки</b>: {is_shortened}\n\n"
        "📝 <b>Розклад уроків:</b>\n\n"
        "{schedule}"
    )


class GetHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.message.register(
            self.get_date,
            GetStates.waiting_for_date
        )

    @classmethod
    @next_state(GetStates.waiting_for_date)
    async def handler(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.HANDLER,
            reply_markup=BackButton().get_keyboard(Triggers.HUB)
        )

    @classmethod
    @with_validation(validate_date)
    async def get_date(cls, message: Message, state: FSMContext, db: DBConnector) -> None:
        date_obj = datetime.strptime(message.text, "%d-%m-%Y").date()
        day = await db.day.get_day(date_obj)

        if day:
            response = Messages.INFO.format(
                day=day.date,
                is_shortened="Так" if day.is_shortened else "Ні",
                schedule=day.call_schedule
            )
        else:
            response = Messages.NO_INFO.format(day=message.text)

        await state.clear()

        await message.answer(
            response,
            reply_markup=BackButton().get_keyboard(Triggers.HUB),
            parse_mode=ParseMode.HTML
        )
