from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters import Command

from ..base import BaseHandler
from src.keyboards.inline import DeveloperHub


class Triggers(str, Enum):
    COMMAND = "dev"
    CALLBACK = "dev_hub"


@dataclass(frozen=True)
class Messages:
    PROMPT: str = (
        "<b>The developer mode has been activated</b>. 🚀"
    )


class DevHubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.show_hub, Command(Triggers.COMMAND))
        self.router.callback_query.register(self.show_hub, F.data == Triggers.CALLBACK)

    @classmethod
    async def show_hub(cls, event: Message | CallbackQuery, state: FSMContext) -> None:
        await state.clear()

        kwargs = {
            "text": Messages.PROMPT,
            "reply_markup": DeveloperHub().get_keyboard(),
            "parse_mode": ParseMode.HTML
        }

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(**kwargs)
        elif isinstance(event, Message):
            await event.answer(**kwargs)
