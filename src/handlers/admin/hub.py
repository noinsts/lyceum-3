from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.keyboards.inline import HubAdmin


class Triggers(str, Enum):
    COMMAND = "admin"
    CALLBACK = "back_to_admin_hub"


@dataclass(frozen=True)
class Messages:
    TITLE = "👑 <b>Вітаємо в панелі адміністратора</b>"


class AdminHubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.show_hub, Command(Triggers.COMMAND))
        self.router.callback_query.register(self.show_hub, F.data == Triggers.COMMAND)

    @classmethod
    async def show_hub(cls, event: Message | CallbackQuery, state: FSMContext) -> None:
        await state.clear()

        kwargs = {
            "text": Messages.TITLE,
            "reply_markup": HubAdmin().get_keyboard(),
            "parse_mode": ParseMode.HTML
        }

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(**kwargs)
        elif isinstance(event, Message):
            await event.answer(**kwargs)
