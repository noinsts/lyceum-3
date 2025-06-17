from enum import Enum
import re

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from .base import BaseHandler
from src.utils import RegisterStates
from src.keyboards.reply import GetType, GetClass, HubMenu, HubTeacher
from src.utils import classes


class UserType(str, Enum):
    STUDENT = "👨‍🎓 Учень"
    TEACHER = "👨‍🏫 Вчитель"
    CMD_START = "/start"


class RegisterHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.start_register,
            Command('register')
        )

        self.router.message.register(
            self.get_type,
            RegisterStates.waiting_for_type
        )

        self.router.message.register(
            self.get_class,
            RegisterStates.waiting_for_class
        )
        self.router.message.register(
            self.get_teacher_name,
            RegisterStates.waiting_for_teacher_name
        )

        self.router.message.register(
            self.finally_register,
            RegisterStates.finally_register
        )

    @staticmethod
    async def start_register(message: Message, state: FSMContext) -> None:
        """Запускає процес реєстрації: питає тип користувача (учень/вчитель)"""
        await message.answer("Хто ви? Оберіть нижче 👇", reply_markup=GetType().get_keyboard())
        await state.set_state(RegisterStates.waiting_for_type)

    @staticmethod
    async def get_type(message: Message, state: FSMContext) -> None:
        """Обробляє вибір типу користувача та переводить FSM на відповідний state"""
        match message.text:
            case UserType.STUDENT.value:
                await state.update_data(user_type="student")
                await state.set_state(RegisterStates.waiting_for_class)
                await message.answer("Зі списку нижче оберіть ваш клас", reply_markup=GetClass().get_keyboard())

            case UserType.TEACHER.value:
                await state.update_data(user_type='teacher')
                await state.set_state(RegisterStates.waiting_for_teacher_name)
                await message.answer("Будь ласка, вкажіть ваше ПІП (повністю)", reply_markup=ReplyKeyboardRemove())

            case UserType.CMD_START.value:
                await state.clear()
                # імпорт в середині циклу задля уникнення циклічного імпорту
                from src.handlers.common import CommonHandler
                await CommonHandler().start_cmd(message, state)

            case _:
                await message.answer("Будь ласка, оберіть варіант, натиснувши на кнопку 👇")
                return

    def normalize_class(self, raw: str) -> str | None:
        """Валідуємо формат класу: цифра (1–12) + українська літера (А–Я)"""

        match = re.match(r"^(\d{1,2})[- ]?([А-ЯІЇЄҐ])$", raw.strip().upper())

        """
        ^         — початок рядка
        (\d{1,2}) — одна або дві цифри (клас)
        [- ]?     — необов’язковий дефіс або пробіл
        [А-ЯІЇЄ]  — одна велика українська літера (паралель класу)
        $         — кінець рядка
        """

        if not match:
            return None

        # Приводимо клас до формату: 9-А → 9-А (з дефісом та великою літерою)
        return f"{int(match.group(1))}-{match.group(2)}"

    async def get_class(self, message: Message, state: FSMContext) -> None:
        """Обробляє введення класу, перевіряє формат, вікове обмеження та наявність класу в базі"""
        user_class = self.normalize_class(message.text)

        # Якщо введено клас у неправильному форматі
        if not user_class:
            await message.answer("А якщо по чесному? Вводь щось типу '9-A' 😉")
            return

        # Якщо клас нижче 5 — користувачу ще рано в Telegram 😅
        if int(user_class.split("-")[0]) < 5:
            await message.answer(
                "Вам дуже мало років для телеграму\n"
                "Будь ласка, видаліть його і не згадуйте до 5-го класу 🌱"
            )
            return

        # перевірка класу чи є він в школі
        if not user_class in classes.CLASSES:
            await message.answer("Такого класу в нас немає. Може, перевірите ще раз? 🤔")
            return

        # Зберігаємо оброблені дані в машині станів (FSM)
        await state.update_data(user_class=user_class)
        await state.set_state(RegisterStates.finally_register)

        # Запускаємо фінальний етап вручну (переведення не через кнопку, а через код)
        await self.finally_register(message, state)

    async def get_teacher_name(self, message: Message, state: FSMContext) -> None:
        """Запит в учителя його ПІП"""
        teacher_name = message.text

        # TODO: Biletska guard

        # Якщо введений ПІП не належить до списку вчителів школи
        if not self.db.register.teacher_checker(teacher_name):
            await message.answer(
                "🚫 Такого ПІП немає в нашому списку вчителів. "
                "Можливо, ви ввели з помилкою або ще не додані до бази.\n"
                "Спробуйте ще раз або зверніться до @noinsts 👨‍💻"
            )
            return

        # інформацію про наявих користувачів в бд
        if self.db.register.clone_teacher(teacher_name):
            await message.answer(
                "💥 <b>Зверніть увагу, хтось з таким ім'я вже зареєстрований. "
                "Це не завадить вам користуватись проектом, "
                "проте якщо вам це не подобається, зверніться до @noinsts</b>",
                parse_mode=ParseMode.HTML
            )

        # Валідуємо хоча б по наявності 3 слів
        if len(teacher_name.split()) < 3:
            await message.answer("ПІП має містити три слова (Прізвище Ім'я По-батькові). Спробуйте ще раз.")
            return

        # Зберігаємо оброблені дані в машині станів (FSM)
        await state.update_data(teacher_name=teacher_name)
        await state.set_state(RegisterStates.finally_register)

        # TODO: тільки на етапі тестування (можливо до жовтня)
        await message.answer(
            "⚠️ <b>Поки що функції для вчителів знаходяться в розробці, можлива наявність помилок та неточностей, "
            "будь-ласка при виявленні таких повідомте тестерів</b>",
            parse_mode=ParseMode.HTML
        )

        # Запускаємо фінальний етап вручну (переведення не через кнопку, а через код)
        await self.finally_register(message, state)

    async def finally_register(self, message: Message, state: FSMContext) -> None:
        """Фінал реєстрації: запис у базу, показ підтвердження та меню користувача"""

        # отримуємо інформацію
        data = await state.get_data()
        user_type = data.get("user_type")
        user_class = data.get("user_class")
        teacher_name = data.get("teacher_name")

        # записуємо інфу в бд
        self.db.register.add_user(
            message.from_user.id,
            user_type,
            message.from_user.full_name,
            message.from_user.username,
            user_class,
            teacher_name
        )

        # створюємо промпт повідомлення
        msg = (
            f"✅ <b>Успіх! Дані успішно записані!</b>\n\n"
            f"<b>Тип:</b> {user_type}\n"
        )
        if user_type == "student":
            msg += f"<b>Клас:</b> {user_class}\n"
        elif user_type == "teacher":
            msg += f"<b>ПІП:</b> {teacher_name}\n"
        msg += "\n❓ Якщо ви зробили одрук, то використайте команду /register для повторної реєстрації"

        # виводимо користувачу
        await message.answer(
            msg,
            reply_markup=HubTeacher().get_keyboard()
            if user_type == UserType.TEACHER
            else HubMenu().get_keyboard(),
            parse_mode=ParseMode.HTML
        )

        # закриваємо FSM
        await state.clear()
