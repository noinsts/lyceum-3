from aiogram.types import ReplyKeyboardMarkup

from src.keyboards.reply import HubMenu, HubTeacher
from src.db.database import Database

db = Database()


def parse_hub_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    user_type = db.register.get_type(user_id)

    match user_type:
        case "student":
            return HubMenu().get_keyboard()
        case "teacher":
            return HubTeacher().get_keyboard()
        case _:
            raise ValueError("Невірний тип користувача")
