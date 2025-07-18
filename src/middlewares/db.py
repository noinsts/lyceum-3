from typing import Callable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.db.db import session_maker
from src.db.connector import DBConnector


class DBMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable,
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        async with session_maker() as session:
            data["db"] = DBConnector(session)
            return await handler(event, data)
