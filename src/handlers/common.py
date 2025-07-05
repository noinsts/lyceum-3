from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from .base import BaseHandler
from src.keyboards.reply import HubMenu, HubTeacher
from src.keyboards.inline import HubAdmin, DeveloperHub
from .register import RegisterHandler
from settings.admins import Admins
from settings.developers import Developers


class CommonHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.start_cmd, CommandStart())

    async def start_cmd(self, message: Message, state: FSMContext) -> None:
        """Обробник команди start"""
        user_id = message.from_user.id

        admins = Admins().ADMINS
        developers = Developers().DEVELOPERS

        if user_id in developers:
            await message.answer(
                "The developer mode has been activated. 🚀",
                reply_markup=DeveloperHub().get_keyboard()
            )

        if self.db.register.checker(user_id):
            # якщо користувач зареєстрований
            user_type = self.db.register.get_type(user_id)

            match user_type:
                case 'student':
                    form = self.db.register.get_class(user_id)
                    prompt = (
                        f"👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                        f"Ви зареєстровані як учень <b>{form}</b> класу.\n\n"
                        f"Якщо хочете змінити дані, використайте команду /register"
                    )
                    rm = HubMenu().get_keyboard()
                case "teacher":
                    teacher_name = self.db.register.get_teacher_name(user_id)
                    prompt = (
                        f"👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                        f"Ви зареєстровані як вчитель <b>{teacher_name}</b>\n\n"
                        f"Якщо хочете змінити дані, використайте команду /register"
                    )
                    rm = HubTeacher().get_keyboard()
                case _:
                    prompt = (
                        "⚠️ Помилка: тип вашого акаунту не розпізнано.\n"
                        "Зверніться до адміністратора або пройдіть реєстрацію заново (/register)"
                    )
                    rm = None

            await message.answer(prompt, reply_markup=rm, parse_mode=ParseMode.HTML)

            if user_id in admins:
                await message.answer(
                    "👑 Панель андміністратора ввікмнена.",
                    reply_markup=HubAdmin().get_keyboard()
                )

        else:
            # якщо користувач не зареєстрований
            await message.answer(
                "👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                "Будь-ласка, зареєструйтеся, щоб скористатись всіма можливостями бота\n\n"
                "⚙️ Telegram-канал бота: поки що відсутній (скоро буде)",
                # TODO: додати посилання на тгк бота, коли буде
                parse_mode=ParseMode.HTML
            )
            await RegisterHandler().start_register(message, state)
