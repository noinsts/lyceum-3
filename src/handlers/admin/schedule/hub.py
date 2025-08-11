from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler
from src.keyboards.inline import HubAdminSchedule


class AdminScheduleHub(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data.in_({'admin_schedule_hub', 'to_admin_schedule_hub'})
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.message.edit_text(
            "Оберіть зі списку нижче, що вас цікавить",
            reply_markup=HubAdminSchedule().get_keyboard()
        )

        await callback.answer()
