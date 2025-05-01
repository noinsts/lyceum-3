from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from .base import BaseHandler
from src.keyboards.reply import HubMenu
from .register import RegisterHandler


class CommonHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.start_cmd, CommandStart())


    async def start_cmd(self, message: Message, state: FSMContext) -> None:
        """Обробник команди start"""
        user_id = message.from_user.id

        if self.db.register.checker(user_id):
            """Якщо користувач зареєстрований"""
            if self.db.register.get_type(user_id) == 'student':
                form = self.db.register.get_class(user_id)
                prompt = (f"👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                          f"Ви зареєстровані як учень <b>{form}</b> класу.\n\n"
                          f"Якщо хочете змінити дані, використайте команду /register")
            else:
                teacher_name = self.db.register.get_teacher_name(user_id)
                prompt = (f"👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                          f"Ви зареєстровані як вчитель <b>{teacher_name}</b>\n\n"
                          f"Якщо хочете змінити дані, використайте команду /register")

            await message.answer(
                prompt,
                reply_markup=HubMenu().get_keyboard(),
                parse_mode=ParseMode.HTML
            )

        else:
            """Відправляємо користувача на реєстрацію"""
            await message.answer(
                "👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                "Будь-ласка, зареєструйтеся, щоб скористатись всіма можливостями бота\n\n"
                "ps: 📢 Бот неофіційний. Його зробив дефолтний учень, а не адміністрація — тому якщо щось глючить, "
                "не пишіть завучу xd. (овнер @noinsts)",
                parse_mode=ParseMode.HTML
            )
            await RegisterHandler().start_register(message, state)
