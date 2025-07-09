from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler
from src.keyboards.inline import DeveloperAccessHub


class AccessHubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'dev_access_hub'
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        # заглушка
        await callback.answer()

        await callback.message.answer(
            "Select next action",
            reply_markup=DeveloperAccessHub().get_keyboard()
        )
