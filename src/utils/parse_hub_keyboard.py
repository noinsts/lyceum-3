from aiogram.types import ReplyKeyboardMarkup

from src.keyboards.reply import HubMenu, HubTeacher
from src.db.db import session_maker
from src.db.connector import DBConnector
from src.enums import DBUserType


async def parse_hub_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    async with session_maker() as session:
        db = DBConnector(session)

        user_type = await db.register.get_type(user_id)

        match user_type:
            case DBUserType.STUDENT:
                return HubMenu().get_keyboard()
            case DBUserType.TEACHER:
                return HubTeacher().get_keyboard()
            case _:
                raise ValueError("Невірний тип користувача")
