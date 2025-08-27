import logging
import time
import traceback
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineQuery

from src.utils import setup_logger

class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логування всіх подій в Telegram боті
    """

    def __init__(self):
        self.logger = setup_logger()
        self.start_times: Dict[str, float] = {}

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        # Унікальний ID для цього запиту
        request_id = f"{int(time.time() * 1000000)}"
        self.start_times[request_id] = time.time()

        # Отримуємо інформацію про користувача та подію
        user_info = self._extract_user_info(event)
        event_info = self._extract_event_info(event)

        # Логуємо початок обробки
        self.logger.info(
            f"[{request_id}] 📥 INCOMING | "
            f"User: {user_info['id']} (@{user_info['username']}) | "
            f"Event: {event_info['type']} | "
            f"Data: {event_info['data']}"
        )

        try:
            # Виконуємо handler
            result = await handler(event, data)

            # Вираховуємо час обробки
            processing_time = time.time() - self.start_times.get(request_id, time.time())

            # Логуємо успішну обробку
            self.logger.info(
                f"[{request_id}] ✅ SUCCESS | "
                f"Time: {processing_time:.3f}s | "
                f"User: {user_info['id']}"
            )

            return result

        except Exception as e:
            # Вираховуємо час обробки навіть при помилці
            processing_time = time.time() - self.start_times.get(request_id, time.time())

            # Логуємо помилку
            self.logger.error(
                f"[{request_id}] ❌ ERROR | "
                f"Time: {processing_time:.3f}s | "
                f"User: {user_info['id']} | "
                f"Exception: {type(e).__name__}: {str(e)}"
            )

            # Детальний traceback для серйозних помилок
            if not isinstance(e, (KeyError, ValueError, AttributeError)):
                self.logger.error(f"[{request_id}] 🔥 TRACEBACK:\n{traceback.format_exc()}")

            # Пробуємо відправити користувачу повідомлення про помилку
            await self._handle_user_error(event, request_id)

            raise  # Перекидаємо помилку далі

        finally:
            # Очищаємо старі start_times
            if request_id in self.start_times:
                del self.start_times[request_id]

    def _extract_user_info(self, event: TelegramObject) -> Dict[str, Any]:
        """Витягуємо інформацію про користувача"""
        user_info = {
            'id': 'unknown',
            'username': 'unknown',
            'first_name': 'unknown',
            'last_name': '',
            'is_bot': False
        }

        user = None
        if hasattr(event, 'from_user') and event.from_user:
            user = event.from_user
        elif hasattr(event, 'message') and event.message and hasattr(event.message, 'from_user'):
            user = event.message.from_user

        if user:
            user_info.update({
                'id': user.id,
                'username': user.username or 'no_username',
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'is_bot': user.is_bot
            })

        return user_info

    def _extract_event_info(self, event: TelegramObject) -> Dict[str, Any]:
        """Витягуємо інформацію про подію"""
        event_info = {
            'type': type(event).__name__,
            'data': '',
            'chat_id': 'unknown',
            'message_id': 'unknown'
        }

        if isinstance(event, Message):
            event_info.update({
                'type': 'Message',
                'data': self._truncate_text(event.text or event.caption or '[media]'),
                'chat_id': event.chat.id,
                'message_id': event.message_id,
                'content_type': event.content_type
            })

            # Додаткова інформація для медіа
            if event.photo:
                event_info['data'] = f"[photo] {event.caption or ''}"
            elif event.document:
                event_info['data'] = f"[document: {event.document.file_name}]"
            elif event.voice:
                event_info['data'] = "[voice message]"

        elif isinstance(event, CallbackQuery):
            event_info.update({
                'type': 'Callback',
                'data': event.data or 'no_data',
                'chat_id': event.message.chat.id if event.message else 'unknown',
                'message_id': event.message.message_id if event.message else 'unknown'
            })

        elif isinstance(event, InlineQuery):
            event_info.update({
                'type': 'InlineQuery',
                'data': self._truncate_text(event.query),
                'chat_id': 'inline',
                'query_id': event.id
            })

        return event_info

    def _truncate_text(self, text: str, max_length: int = 100) -> str:
        """Обрізаємо довгий текст для логів"""
        if not text:
            return '[empty]'

        if len(text) <= max_length:
            return text

        return f"{text[:max_length]}..."

    async def _handle_user_error(self, event: TelegramObject, request_id: str):
        """Спробуємо відправити користувачу повідомлення про помилку"""
        try:
            if isinstance(event, Message) and event.bot:
                await event.bot.send_message(
                    event.chat.id,
                    "😔 Виникла помилка під час обробки вашого запиту. "
                    f"Спробуйте ще раз або зверніться до адміністратора.\n"
                    f"ID помилки: {request_id}\n\n"
                    "Для допомоги можете написати в дірект @omyzsh"
                )
            elif isinstance(event, CallbackQuery) and event.bot:
                await event.answer(
                    "😔 Виникла помилка. Спробуйте ще раз.",
                    show_alert=True
                )
        except Exception as e:
            self.logger.warning(f"[{request_id}] Failed to send error message to user: {e}")


# Додатковий middleware для збору статистики
class StatsMiddleware(BaseMiddleware):
    """
    Middleware для збору статистики використання
    """

    def __init__(self):
        self.logger = logging.getLogger("telegram_bot_stats")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        # Збираємо статистику перед обробкою
        user_id = None
        event_type = type(event).__name__

        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message:
            user_id = event.message.from_user.id

        # Логуємо статистику (можна пізніше парсити для аналітики)
        self.logger.info(
            f"STATS | User: {user_id} | Event: {event_type} | "
            f"Timestamp: {int(time.time())}"
        )

        return await handler(event, data)
