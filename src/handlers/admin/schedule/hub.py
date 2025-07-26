from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler
from src.keyboards.inline import HubAdminSchedule


class AdminScheduleHub(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'admin_schedule_hub'
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.message.answer(
            "Оберіть зі списку нижче, що вас цікавить",
            reply_markup=HubAdminSchedule().get_keyboard()
        )

        await callback.answer()
