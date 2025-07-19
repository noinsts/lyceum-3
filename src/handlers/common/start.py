from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from src.db.connector import DBConnector
from src.enums import DBUserType
from src.handlers.base import BaseHandler
from src.keyboards.reply import HubMenu, HubTeacher
from src.keyboards.inline import HubAdmin, DeveloperHub
from src.handlers.common.register import RegisterHandler
from settings.admins import Admins
from settings.developers import Developers


class StartHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.start_cmd, CommandStart())

    @staticmethod
    async def start_cmd(message: Message, state: FSMContext, db: DBConnector) -> None:
        """Обробник команди start"""
        user_id = message.from_user.id

        admins = Admins().ADMINS
        developers = Developers().DEVELOPERS

        if user_id in developers:
            await message.answer(
                "The developer mode has been activated. 🚀",
                reply_markup=DeveloperHub().get_keyboard()
            )

        if await db.register.is_exists(user_id):
            # якщо користувач зареєстрований
            user_type = await db.register.get_user_type(user_id)

            match user_type:
                case DBUserType.STUDENT:
                    form = await db.register.get_form(user_id)
                    student_name = await db.register.get_student_name(user_id)
                    prompt = (
                        f"👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                        f"Ви зареєстровані як {student_name}, учень(-ця) <b>{form}</b> класу.\n\n"
                        f"Якщо хочете змінити дані, використайте команду /register"
                    )
                    rm = HubMenu().get_keyboard()
                case "teacher":
                    teacher_name = await db.register.get_teacher_name(user_id)
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
                    "👑 Панель адміністратора ввімкнена.",
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
