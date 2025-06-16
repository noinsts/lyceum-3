from abc import ABC, abstractmethod

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup


class BaseKeyboard(ABC):
    @abstractmethod
    def get_keyboard(self) -> ReplyKeyboardMarkup | InlineKeyboardMarkup:
        pass
