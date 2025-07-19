import inspect
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
        # Витягуємо callback із HandlerObject, якщо це він
        real_handler = getattr(data.get("handler"), "callback", handler)

        try:
            signature = inspect.signature(real_handler)
            needs_db = "db" in signature.parameters
        except (TypeError, ValueError):
            # Якщо не вдалося прочитати — граємось на безпеку
            needs_db = True

        if not needs_db:
            return await handler(event, data)

        async with session_maker() as session:
            data["db"] = DBConnector(session)
            return await handler(event, data)
