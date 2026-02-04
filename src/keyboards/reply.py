from typing import List, Optional

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from .base import BaseKeyboard
from src.enums import OlympStage


class UniversalKeyboard(BaseKeyboard):
    def get_keyboard(self, arr: Optional[List] = None) -> ReplyKeyboardMarkup:
        kb = [[KeyboardButton(text=obj) for obj in arr]]
        return ReplyKeyboardMarkup(keyboard=kb)


class GetClass(BaseKeyboard):
    def get_keyboard(self, classes: Optional[List] = None) -> ReplyKeyboardMarkup:
        keyboard_buttons = []
        row = []

        for i, class_name in enumerate(classes):
            row.append(KeyboardButton(text=class_name))
            if len(row) == 3 or i == len(classes) - 1:
                keyboard_buttons.append(row)
                row = []

        return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)


"""HUB"""


class HubMenu(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        kb = [
            [KeyboardButton(text='📅 Розклад на сьогодні'), KeyboardButton(text='🌇 Розклад на завтра')],
            [KeyboardButton(text='🔔 Розклад дзвінків'), KeyboardButton(text='📝 Розклад на весь тиждень')],
            [KeyboardButton(text='🌐 Ресурси школи'), KeyboardButton(text='🤓 Олімпіади')]
        ]
        return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


class HubTeacher(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        kb = [
            [KeyboardButton(text='🚦 Мій пост'), KeyboardButton(text='📅 Класи на сьогодні')],
            [KeyboardButton(text='📝 Тижневий розклад'), KeyboardButton(text='🌅 Розклад на завтра')],
            [KeyboardButton(text='🔔 Розклад дзвінків'), KeyboardButton(text='🌐 Ресурси школи')],
            [KeyboardButton(text="👥 Мій клас")],
            [KeyboardButton(text='⏰ Кількість академічних годин'), KeyboardButton(text='🚀 Хаб олімпіад')]
        ]
        return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


class SkipButton(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        kb = [
            [KeyboardButton(text='🚫 Пропустити')]
        ]

        return ReplyKeyboardMarkup(keyboard=kb)


class OlympStages(BaseKeyboard):
    def get_keyboard(self) -> ReplyKeyboardMarkup:
        kb = [[KeyboardButton(text=stage.value) for stage in OlympStage.__members__.values()]]
        return ReplyKeyboardMarkup(keyboard=kb)
