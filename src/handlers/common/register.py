from enum import Enum
import re

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from src.db.connector import DBConnector
from src.db.schemas import AddUserSchema
from src.handlers.base import BaseHandler
from src.utils import RegisterStates, classes, parse_hub_keyboard
from src.keyboards.reply import GetType, GetClass, HubMenu, HubTeacher
from src.enums import DBUserType


USER_TYPE_PRETTY = {
    "student": "Учень",
    "teacher": "Вчитель"
}


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
            self.get_student_name,
            RegisterStates.waiting_for_student_name
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
    async def get_type(message: Message, state: FSMContext, db: DBConnector) -> None:
        """Обробляє вибір типу користувача та переводить FSM на відповідний state"""
        match message.text:
            case UserType.STUDENT.value:
                await state.update_data(user_type=DBUserType.STUDENT)
                await state.set_state(RegisterStates.waiting_for_class)
                await message.answer(
                    "Зі списку нижче оберіть ваш клас",
                    reply_markup=GetClass().get_keyboard(classes.CLASSES)
                )

            case UserType.TEACHER.value:
                await state.update_data(user_type=DBUserType.TEACHER)
                await state.set_state(RegisterStates.waiting_for_teacher_name)
                await message.answer("Будь ласка, вкажіть ваше ПІП (повністю)", reply_markup=ReplyKeyboardRemove())

            case UserType.CMD_START.value:
                await state.clear()
                # імпорт в середині циклу задля уникнення циклічного імпорту
                from .start import StartHandler
                await StartHandler().start_cmd(message, state, db)

            case _:
                await message.answer("Будь ласка, оберіть варіант, натиснувши на кнопку 👇")
                return

    @staticmethod
    def normalize_class(raw: str) -> str | None:
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

        # TODO: винести в src/utils/

    async def get_class(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        """Обробляє введення класу, перевіряє формат, вікове обмеження та наявність класу в базі"""
        form = self.normalize_class(message.text)

        # Якщо введено клас у неправильному форматі
        if not form:
            await message.answer("А якщо по чесному? Вводь щось типу '9-A' 😉")
            return

        # Якщо клас нижче 5 — користувачу ще рано в Telegram 😅
        if int(form.split("-")[0]) < 5:
            await message.answer(
                "Вам дуже мало років для телеграму\n"
                "Будь ласка, видаліть його і не згадуйте до 5-го класу 🌱"
            )
            return

        # перевірка класу чи є він в школі
        if form not in classes.CLASSES:
            await message.answer("Такого класу в нас немає. Може, перевірите ще раз? 🤔")
            return

        # Зберігаємо оброблені дані в машині станів (FSM)
        await state.update_data(form=form)
        await state.set_state(RegisterStates.waiting_for_student_name)

        # відправляємо feedback
        await message.answer("Добре, тепер введіть ваше прізвище та ім'я, наприклад: Лепський Артем")

    async def get_student_name(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        student_name = message.text

        # TODO: додати валідатори та парсери student_name

        await state.update_data(student_name=student_name)
        await state.set_state(RegisterStates.finally_register)

        # Запускаємо фінальний етап вручну (переведення не через кнопку, а через код)
        await self.finally_register(message, state, db)

    async def get_teacher_name(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        """Запит в учителя його ПІП"""
        teacher_name = message.text

        # TODO: Biletska guard

        # TODO: зробить teacher checker

        # Якщо введений ПІП не належить до списку вчителів школи
        # if not self.db.register.teacher_checker(teacher_name):
        #     await message.answer(
        #         "🚫 Такого ПІП немає в нашому списку вчителів. "
        #         "Можливо, ви ввели з помилкою або ще не додані до бази.\n"
        #         "Спробуйте ще раз або зверніться до @noinsts 👨‍💻"
        #     )
        #     return

        # TODO: зробить тут

        # інформацію про наявих користувачів в бд
        if await db.register.clone_teacher(teacher_name):
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
        await self.finally_register(message, state, db)

    @staticmethod
    async def finally_register(message: Message, state: FSMContext, db: DBConnector) -> None:
        """Фінал реєстрації: запис у базу, показ підтвердження та меню користувача"""

        # отримуємо інформацію
        data = await state.get_data()
        user_type = data.get("user_type")
        form = data.get("form")
        teacher_name = data.get("teacher_name")
        student_name = data.get("student_name")

        # записуємо інфу в бд
        await db.register.add_user(
            AddUserSchema(
                user_id=int(message.from_user.id),
                full_name=message.from_user.full_name,
                username=message.from_user.username,
                user_type=user_type,
                form=form,
                teacher_name=teacher_name,
                student_name=student_name
            )
        )

        # створюємо промпт повідомлення
        msg = (
            f"✅ <b>Успіх! Дані успішно записані!</b>\n\n"
            f"<b>Тип:</b> {USER_TYPE_PRETTY.get(user_type, user_type)}\n"
        )
        if user_type == "student":
            msg += (f"<b>Клас</b>: {form}\n"
                    f"<b>Ім'я</b>: {student_name}")
        elif user_type == "teacher":
            msg += f"<b>ПІП:</b> {teacher_name}\n"
        msg += "\n❓ Якщо ви зробили одрук, то використайте команду /register для повторної реєстрації"

        # виводимо користувачу
        await message.answer(
            msg,
            reply_markup=await parse_hub_keyboard(message.from_user.id),
            parse_mode=ParseMode.HTML
        )

        # закриваємо FSM
        await state.clear()
