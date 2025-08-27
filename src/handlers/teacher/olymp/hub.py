from aiogram import F
from aiogram.types import Message

from ...base import BaseHandler
from src.keyboards.inline import TeacherOlympHub


class OlympHub(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.olymp_hub, F.text == '🚀 Хаб олімпіад')

    @staticmethod
    async def olymp_hub(message: Message) -> None:
        await message.answer(
            "Вітаємо в хабі олімпіад. Оберіть що вас цікавить 👇🏻",
            reply_markup=TeacherOlympHub().get_keyboard()
        )
