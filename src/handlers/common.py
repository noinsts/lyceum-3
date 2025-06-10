from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from .base import BaseHandler
from src.keyboards.reply import HubMenu, HubTeacher
from .register import RegisterHandler
from src.settings.admins import Admins


class CommonHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.start_cmd, CommandStart())


    async def start_cmd(self, message: Message, state: FSMContext) -> None:
        """Обробник команди start"""
        user_id = message.from_user.id

        if user_id in Admins().ADMINDS:
            await message.answer(
                "<b>👋 Вітаємо в чат-боті Березанського ліцею №3!</b>\n\n"
                "Ви зареєстровані як <b>адміністратор ЗЗСО</b>. Тепер ви можете:\n\n"
                "• надсилати зміни в розкладі;\n"
                "• надсилати оголошення учням та вчителям;\n"
                "• заплановувати наради.\n\n"
                "📽 Щоб ознайомитися з роботою бота, будь ласка, перегляньте відео нижче.",
                parse_mode=ParseMode.HTML
            )
            return

        if self.db.register.checker(user_id):
            """Якщо користувач зареєстрований"""
            if self.db.register.get_type(user_id) == 'student':
                form = self.db.register.get_class(user_id)
                prompt = (f"👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                          f"Ви зареєстровані як учень <b>{form}</b> класу.\n\n"
                          f"Якщо хочете змінити дані, використайте команду /register")
                rm = HubMenu().get_keyboard()
            else:
                teacher_name = self.db.register.get_teacher_name(user_id)
                prompt = (f"👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                          f"Ви зареєстровані як вчитель <b>{teacher_name}</b>\n\n"
                          f"Якщо хочете змінити дані, використайте команду /register")
                rm = HubTeacher().get_keyboard()

            await message.answer(
                prompt,
                reply_markup=rm,
                parse_mode=ParseMode.HTML
            )

        else:
            """Відправляємо користувача на реєстрацію"""
            await message.answer(
                "👋🏻 Вітаємо в чат-боті <b>Березанського ліцею №3</b>\n\n"
                "Будь-ласка, зареєструйтеся, щоб скористатись всіма можливостями бота\n\n"
                "📢 Бот неофіційний. Його зробив дефолтний учень, а не адміністрація — тому якщо щось глючить, "
                "не пишіть завучу xd. (овнер @noinsts)\n\n"
                "ℹ️ Розклад був отриманий з оф. сайту школи (bnvk.pp.ua)",
                parse_mode=ParseMode.HTML
            )
            await RegisterHandler().start_register(message, state)
