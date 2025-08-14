from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from ..base import BaseHandler
from src.keyboards.inline import DeveloperHub


class DevHubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.show_hub,
            Command("dev")
        )

        self.router.callback_query.register(
            self.show_hub,
            F.data == "dev_hub"
        )

    @classmethod
    async def show_hub(cls, event: Message | CallbackQuery, state: FSMContext) -> None:
        await state.clear()

        prompt = "The developer mode has been activated. 🚀"
        rm = DeveloperHub().get_keyboard()

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(prompt, reply_markup=rm)
        else:
            await event.answer(prompt, reply_markup=rm)
