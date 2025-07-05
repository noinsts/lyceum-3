from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

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
            [InlineKeyboardButton(text='Зміна розкладу (ВЧИТЕЛІ)', callback_data='teachers_change_schedule')],
            [InlineKeyboardButton(text='🫱🏻‍🫲🏻 Запланувати нараду', callback_data='meeting')],
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class TeacherTypes(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='Початкових класів', callback_data='teacher_primary')],
            [InlineKeyboardButton(text='Середньої ланки', callback_data='teacher_middle')],
            [InlineKeyboardButton(text='Старших класів', callback_data='teacher_senior')],
            [InlineKeyboardButton(text='Асистенти-вчителі', callback_data='teacher_assistant')],
            [InlineKeyboardButton(text='Іноземні мови', callback_data='teacher_foreign')],
            [InlineKeyboardButton(text='Інклюзивна освіта', callback_data='teacher_inclusive')],
            [InlineKeyboardButton(text='Вч. історії, правознавства та гром. освіти', callback_data='teacher_social_studies')],
            [InlineKeyboardButton(text='Математики, програмісти 😏', callback_data='teacher_stem')],
            [InlineKeyboardButton(text='Філологи', callback_data='teacher_philology')],
            [InlineKeyboardButton(text='Природничі дисципліни', callback_data='teacher_natural_sciences')],
            [InlineKeyboardButton(text='Вчителі фізичної культури', callback_data='teacher_sport')],
            [InlineKeyboardButton(text='✅ Готово', callback_data='meeting_submit_button')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class SubmitKeyboard(BaseKeyboard):
    def get_keyboard(self, submit_cb: str = "submit", cancel_cb: str ="cancel") -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='✅ Так, підтвердити', callback_data=submit_cb)],
            [InlineKeyboardButton(text='❌ Ні, почати заповнювати наново', callback_data=cancel_cb)]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class TeacherOlympHub(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='Створити нову олімпіаду', callback_data='create_new_olymp')],
            [InlineKeyboardButton(text='Редагувати наявну', callback_data='edit_olymp')],
            [InlineKeyboardButton(text='Видалити', callback_data='delete_olymp')],
            [InlineKeyboardButton(text='Список олімпіад', callback_data='list_olymps')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)
