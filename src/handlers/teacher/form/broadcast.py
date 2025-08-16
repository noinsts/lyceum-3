from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
# from aiogram.enums import ParseMode

from ...base import BaseHandler


class Triggers(str, Enum):
    HANDLER = "my_form_broadcast"


@dataclass(frozen=True)
class Messages:
    DEV_MODE: str = (
        "👷🏻 Ця кнопка ще будується"
    )


class BroadcastHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.answer(Messages.DEV_MODE, show_alert=True)
