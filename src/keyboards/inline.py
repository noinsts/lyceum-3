from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .base import BaseKeyboard


class HubAdmin(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='📢 Створити оголошення', callback_data="announcement_hub")]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class AdminAnnouncementHub(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='Зміна розкладу (СТУДЕНТИ)', callback_data='students_change_schedule')],
            [InlineKeyboardButton(text='Зміна розкладу (ВЧИТЕЛІ)', callback_data='teachers_change_schedule')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)
