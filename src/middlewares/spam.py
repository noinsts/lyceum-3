from typing import Callable, Dict, Any
import time

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.utils import setup_logger

logger = setup_logger()


class AntiSpamMiddleware(BaseMiddleware):
    """
    Запобігання спаму в боті
    """

    def __init__(self, timeout: float = 1.0) -> None:
        """
        Args:
            timeout: Час очікування між повідомленнями в секундах
        """

        self.timeout = timeout
        self.user_times: Dict[int, float] = {}
        self.last_cleanup = time.time()

        super().__init__()

    async def __call__(
            self,
            handler: Callable,
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if time.time() - self.last_cleanup > 300:
            self.cleanup_old_users()
            self.last_cleanup = time.time()

        user_id = event.from_user.id
        now = time.time()

        if user_id in self.user_times:
            time_passed = now - self.user_times[user_id]

            if time_passed < self.timeout:
                text = "Не спамте, будь ласка"

                logger.warning(
                    f"{user_id} // {event.from_user.first_name or "pass"}, "
                    f"{event.from_user.username or "pass"} is spamming"
                )

                if isinstance(event, Message):
                    await event.answer(text)
                elif isinstance(event, CallbackQuery):
                    await event.answer(text, show_alert=True)

                return None

        self.user_times[user_id] = now

        return await handler(event, data)

    def cleanup_old_users(self, max_age: float = 3600):
        """Очищує старі записи"""
        now = time.time()
        old_users = [uid for uid, last_time in self.user_times.items() if now - last_time > max_age]
        for uid in old_users:
            self.user_times.pop(uid)
