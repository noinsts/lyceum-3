from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

from ..base import BaseHandler


class HelpHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.handler, Command("help"))

    @staticmethod
    async def handler(message: Message) -> None:
        await message.answer(
            "<b>Lyceum-3</b> — це бот створений для учнів та вчителів <b>Березанського ліцею №3</b>.",
            # TODO: змінити текст, додати inline клавіатуру
            parse_mode=ParseMode.HTML
        )
