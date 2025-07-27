from typing import Optional

from aiogram import Bot

_bot_instance: Optional[Bot] = None


def set_bot(bot: Bot) -> None:
    """Встановлює глобальний екземпляр бота"""
    global _bot_instance
    _bot_instance = bot


def get_bot() -> Bot:
    if _bot_instance is None:
        raise RuntimeError("Bot instance not initialize. Call set_bot() first.")
    return _bot_instance
