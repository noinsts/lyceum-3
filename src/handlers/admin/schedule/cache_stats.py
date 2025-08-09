from dataclasses import dataclass
from enum import Enum

from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler


class Triggers(str, Enum):
    HANDLER = "redis_cache_stats"


@dataclass(frozen=True)
class Messages:
    IN_PROCESS = (
        "🏗️ В розробці..."
    )


class CacheStatsHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery) -> None:
        await callback.answer(Messages.IN_PROCESS)
