from abc import ABC, abstractmethod

from aiogram.types import ReplyKeyboardMarkup


class BaseKeyboard(ABC):
    @abstractmethod
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        pass
