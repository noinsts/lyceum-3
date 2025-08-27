from typing import List, Tuple

import asyncio
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from src.bot_instance import get_bot


async def _send_message(bot, user_id: int, prompt: str) -> bool:
    """
    Службова функція. що намагається надіслати повідомлення користувачу

    Args:
        bot: екземляр Telegram-боту
        user_id (int): Telegram ID користувача
        prompt (str): текст повідомлення з HTML-розміткою

    Returns:
        bool: True, якщо повідомлення успішно надіслано, False - інакше
    """
    try:
        await bot.send_message(user_id, prompt, parse_mode=ParseMode.HTML)
        return True
    except (TelegramBadRequest, TelegramForbiddenError):
        return False


async def broadcast(prompt: str, users_ids: List[int]) -> Tuple[int, int]:
    """
    Надсилає повідомлення всім користувачам зі списку та повертає статистику доставляння.

    Args:
        prompt (str): текст повідомлення, яке потрібно надіслати. Підтримує HTML-розмітку
        users_ids (List[int]): список Telegram ID користувачів, котрим треба відправити сповіщення

    Returns:
        Tuple[int, int]: Кортеж з двох чисел:
            - кількість успішно доставлених повідомлень
            - кількість невдалих спроб (наприклад, бот заблокований або користувача не існує)
    """
    bot = get_bot()
    results = await asyncio.gather(
        *[_send_message(bot, user_id, prompt) for user_id in users_ids]
    )

    count = sum(results)
    failed = len(results) - count
    return count, failed
