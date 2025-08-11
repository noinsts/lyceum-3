from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler
from src.keyboards.inline import AdminAnnouncementHub


class AnnouncementHub(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.announcement_hub,
            F.data == 'announcement_hub'
        )

    @staticmethod
    async def announcement_hub(callback: CallbackQuery):
        await callback.message.edit_text(
            "Оберіть зі списку нижче тип оголошення",
            reply_markup=AdminAnnouncementHub().get_keyboard()
        )

        # заглушка
        await callback.answer()
