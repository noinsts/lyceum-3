from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from .base import BaseKeyboard
from src.utils import classes

"""Registration"""

class GetType(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        kb = [
            [KeyboardButton(text='👨‍🎓 Учень'), KeyboardButton(text='👨‍🏫 Вчитель')]
        ]
        return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


class GetClass(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        keyboard_buttons = []
        row = []

        for i, class_name in enumerate(classes.CLASSES):
            row.append(KeyboardButton(text=class_name))
            if len(row) == 3 or i == len(classes.CLASSES) - 1:
                keyboard_buttons.append(row)
                row = []

        return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)


"""HUB"""

class HubMenu(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        kb = [
            [KeyboardButton(text='➡️ Наступний урок'), KeyboardButton(text='🔔 Розклад дзвінків')],
            [KeyboardButton(text='📅 Розклад на сьогодні'), KeyboardButton(text='🌇 Розклад на завтра')]
        ]
        return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
