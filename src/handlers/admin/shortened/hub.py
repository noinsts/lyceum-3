from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...base import BaseHandler
from src.keyboards.inline import HubAdminShortened


class Triggers(str, Enum):
    HANDLER = "admin_shortened_hub"


@dataclass(frozen=True)
class Messages:
    HANDLER: str = (
        "Оберіть що вас цікавить"
    )


class HubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.message.edit_text(
            Messages.HANDLER,
            reply_markup=HubAdminShortened().get_keyboard()
        )
