from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.keyboards.inline import Resources


class Triggers(str, Enum):
    HANDLER = "🌐 Ресурси школи"


@dataclass(frozen=True)
class Messages:
    TITLE: str = "<b>Ось корисні посилання, щоб завжди бути в курсі шкільних подій</b>"


class ResourcesHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            Messages.TITLE,
            parse_mode=ParseMode.HTML,
            reply_markup=Resources().get_keyboard()
        )
