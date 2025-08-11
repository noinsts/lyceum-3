from enum import Enum

from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler
from src.keyboards.inline import FormControllerAdmin


class Triggers(str, Enum):
    HANDLER = "admin_form_controller_hub"


class FormHubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER.value
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery) -> None:
        await callback.message.edit_text(
            "Оберіть що вас цікавить 👇🏻",
            reply_markup=FormControllerAdmin().get_keyboard()
        )
