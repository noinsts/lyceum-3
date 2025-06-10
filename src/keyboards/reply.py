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
            [KeyboardButton(text='📅 Розклад на сьогодні'), KeyboardButton(text='🌇 Розклад на завтра')],
            [KeyboardButton(text='📝 Розклад на весь тиждень'), KeyboardButton(text='🌎 Цікава кнопка')],
            [KeyboardButton(text='🌐 Ресурси школи'), KeyboardButton(text='❓ Сьогодні скорочені уроки?')]
        ]
        return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


class HubTeacher(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        kb = [
            [KeyboardButton(text='🚦 Мій пост'), KeyboardButton(text='📅 Класи на сьогодні')],
            [KeyboardButton(text='📝 Тижневий розклад'), KeyboardButton(text='🌅 Розклад на завтра')],
            [KeyboardButton(text='🔔 Розклад дзвінків'), KeyboardButton(text='🌐 Ресурси школи'), KeyboardButton(text='❓ Сьогодні скорочені уроки?')],
            [KeyboardButton(text='⏰ Кількість академічних годин')]
        ]
        return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


class HubStats(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        kb = [
            [KeyboardButton(text='Статистика зареєстрованих учасників по класах')]
        ]
        return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
