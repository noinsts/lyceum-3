from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...base import BaseHandler
from src.keyboards.inline import HubAdminSchedule


class Triggers(str, Enum):
    HUB1 = "admin_schedule_hub"
    HUB2 = "to_admin_schedule_hub"


@dataclass(frozen=True)
class Messages:
    HANDLER: str = (
        "Оберіть зі списку нижче, що вас цікавить"
    )


class AdminScheduleHub(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data.in_({Triggers.HUB1, Triggers.HUB2})
        )

    @staticmethod
    async def handler(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.message.edit_text(
            Messages.HANDLER,
            reply_markup=HubAdminSchedule().get_keyboard()
        )
