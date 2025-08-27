from dataclasses import dataclass
from enum import Enum

from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler
from src.keyboards.inline import RedisControlPanel
from src.sheets.connector import refresh_all_schedule


class Triggers(str, Enum):
    HANDLER = "refresh_cache_schedule"


@dataclass(frozen=True)
class Messages:
    REFRESHING = (
        "🔃 Refreshing..."
    )

    DONE = (
        "✅ Cache refreshed successfully!"
    )

    ERROR = (
        "⚠️ Cache refresh completed with errors"
    )


class RefreshHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery) -> None:
        await callback.answer(Messages.REFRESHING)

        success = await refresh_all_schedule()

        response = Messages.DONE if success else Messages.ERROR

        await callback.message.answer(
            response,
            reply_markup=RedisControlPanel().get_keyboard()
        )
