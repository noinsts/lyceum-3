from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from ..base import BaseHandler
from src.keyboards.inline import HubAdmin


class AdminHubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.show_hub,
            Command("admin")
        )

        self.router.callback_query.register(
            self.show_hub,
            F.data == "back_to_admin_hub"
        )

    @classmethod
    async def show_hub(cls, event: Message | CallbackQuery) -> None:
        text = "👑 Вітаємо в панелі адміністратора"
        kb = HubAdmin().get_keyboard()

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(text, reply_markup=kb)
        else:
            await event.answer(text, reply_markup=kb)
