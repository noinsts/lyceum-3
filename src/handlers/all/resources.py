from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ..base import BaseHandler


class Triggers(str, Enum):
    HANDLER = "🌐 Ресурси школи"


@dataclass(frozen=True)
class Messages:
    PROMPT: str = (
        "<b>Ось корисні посилання, щоб завжди бути в курсі шкільних подій</b>:\n\n"
        "🔹 Сайт школи: <a href=\"https://bnvk.pp.ua\">bnvk.pp.ua</a>\n"
        "🔹 Facebook-група: тут публікуються найсвіжіші новини — "
        "<a href=\"https://www.facebook.com/profile.php?id=100035666301370\">перейти</a>\n"
        "🔹 Telegram-канал (неофіційний): <a href=\"https://t.me/projects_noinsts\">тик</a>"
    )
    # TODO: замінить лінк на тгк


class ResourcesHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(Messages.PROMPT, parse_mode=ParseMode.HTML)
