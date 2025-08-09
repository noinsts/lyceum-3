from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler
from src.keyboards.inline import DeveloperAccessHub


class Triggers:
    HANDLER = "dev_access_hub"


class Messages:
    ASCII = r"""
    
    (dev)
    
        _                   
       /_\  __ __ ___ ______
      / _ \/ _/ _/ -_|_-<_-<
     /_/ \_\__\__\___/__/__/
                            
    """


class AccessHubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    @staticmethod
    async def handler(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            Messages.ASCII,
            reply_markup=DeveloperAccessHub().get_keyboard()
        )
