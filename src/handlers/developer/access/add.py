import re

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from src.db.connector import DBConnector
from ...base import BaseHandler
from src.utils.states import DevAddAccess
from src.keyboards.inline import SubmitKeyboard


class AddAccessHandler(BaseHandler):
    # Константи для валідації
    MIN_USER_ID = 1
    MAX_USER_ID = 9999999999  # Максимальний user_id в Telegram
    MIN_TEACHER_NAME_LENGTH = 2
    MAX_TEACHER_NAME_LENGTH = 50

    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'dev_access_add'
        )

        self.router.message.register(
            self.collect_data,
            DevAddAccess.waiting_for_data
        )

        self.router.callback_query.register(
            self.submit,
            DevAddAccess.waiting_for_confirmation,
            F.data == 'add_access_submit'
        )

        self.router.callback_query.register(
            self.cancel,
            DevAddAccess.waiting_for_confirmation,
            F.data == 'add_access_cancel'
        )

    @staticmethod
    async def handler(callback: CallbackQuery, state: FSMContext) -> None:
        """Обробка стартового callback"""
        await callback.answer()

        await callback.message.answer(
            "<b>📝 Додавання доступу</b>\n\n"
            "Введіть дані у такому форматі:\n\n"
            "<code>12345678</code>\n"
            "<code>teacher_name</code>\n\n"
            "<i>Де перший рядок - user_id (тільки цифри), "
            "другий рядок - ім'я вчителя</i>",
            parse_mode=ParseMode.HTML
        )

        await state.set_state(DevAddAccess.waiting_for_data)

    async def collect_data(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        """Валідуємо дані від користувача"""
        if not message.text:
            await message.answer("⚠️ Будь ласка, введіть текстові дані")
            return

        lines = [line.strip() for line in message.text.split("\n") if line.strip()]

        # оброблюємо помилка
        if len(lines) < 2:
            await message.answer("⚠️ Очікується більше інформації (user_id та teacher_name)")
            return

        if len(lines) > 2:
            await message.answer("⚠️ Забагато рядків. Введіть тільки user_id та teacher_name")
            return

        user_id, tn = lines[0], lines[1]

        # валідуємо user_id
        userid_valid_error = self._validate_user_id(user_id)
        if userid_valid_error:
            await message.answer(userid_valid_error, parse_mode=ParseMode.HTML)
            return

        # валідуємо teacher_name
        teacher_name_valid_error = self._validate_teacher_name(tn)
        if teacher_name_valid_error:
            await message.answer(teacher_name_valid_error, parse_mode=ParseMode.HTML)
            return

        # відправляємо інформацію
        await state.update_data(
            user_id=int(user_id),
            teacher_name=tn
        )

        try:
            existing_teacher = await db.verification.get_name(int(user_id))

            if existing_teacher:
                prompt = (
                    "<b>⚠️ Попередження</b>\n\n"
                    f"Акаунт з <code>user_id = {user_id}</code> вже існує.\n"
                    f"Ім'я вчителя буде <b>оновлено</b> з "
                    f"<code>{existing_teacher}</code> на <code>{tn}</code>.\n\n"
                    "<i>Продовжити?</i>"
                )
            else:
                prompt = (
                    "<b>📋 Підтвердження даних</b>\n\n"
                    f"<b>User ID:</b> <code>{user_id}</code>\n"
                    f"<b>Ім'я вчителя:</b> <code>{tn}</code>\n\n"
                    "<i>Все правильно?</i>"
                )
        except Exception as e:
            await message.answer(
                "❌ <b>Помилка бази даних</b>\n\n"
                "Спробуйте пізніше або зверніться до адміністратора.",
                parse_mode=ParseMode.HTML
            )
            self.log.error(f"Помилка під час devmode/access/add: {e}")
            await state.clear()
            return

        # відправляємо фідбек користувачу
        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=SubmitKeyboard().get_keyboard(
                submit_cb="add_access_submit",
                cancel_cb="add_access_cancel"
            )
        )

        # встановлюємо стан для збору callback
        await state.set_state(DevAddAccess.waiting_for_confirmation)

    def _validate_user_id(self, user_id_str: str) -> str | None:
        """Валідація user_id"""
        if not user_id_str:
            return "⚠️ <b>User ID не може бути пустим</b>"

        if not user_id_str.isdigit():
            return (
                "⚠️ <b>Некоректний User ID</b>\n\n"
                "User ID повинен містити тільки цифри.\n"
                f"Ви ввели: <code>{user_id_str}</code>"
            )

        user_id = int(user_id_str)

        if user_id < self.MIN_USER_ID:
            return f"⚠️ <b>User ID занадто малий</b>\n\nМінімальне значення: {self.MIN_USER_ID}"

        if user_id > self.MAX_USER_ID:
            return f"⚠️ <b>User ID занадто великий</b>\n\nМаксимальне значення: {self.MAX_USER_ID}"

        return None

    def _validate_teacher_name(self, teacher_name: str) -> str | None:
        """Валідація імені вчителя"""
        if not teacher_name:
            return "⚠️ <b>Ім'я вчителя не може бути пустим</b>"

        if len(teacher_name) < self.MIN_TEACHER_NAME_LENGTH:
            return (
                f"⚠️ <b>Ім'я вчителя занадто коротке</b>\n\n"
                f"Мінімальна довжина: {self.MIN_TEACHER_NAME_LENGTH} символи"
            )

        if len(teacher_name) > self.MAX_TEACHER_NAME_LENGTH:
            return (
                f"⚠️ <b>Ім'я вчителя занадто довге</b>\n\n"
                f"Максимальна довжина: {self.MAX_TEACHER_NAME_LENGTH} символів"
            )

        # Перевірка на заборонені символи
        if not re.match(r"^[а-щА-ЩЬьЮюЯяІіЇїЄєҐґA-Za-z\s'\-]+$", teacher_name):
            return "⚠️ <b>Ім'я вчителя має містити тільки літери, пробіли, апостроф або дефіс</b>"

        # Перевірка на тільки пробіли
        if teacher_name.isspace():
            return "⚠️ <b>Ім'я вчителя не може складатися тільки з пробілів</b>"

        return None

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        """Обробка callback погодження"""
        await callback.answer()

        try:
            data = await state.get_data()
            user_id = data.get("user_id")
            teacher_name = data.get("teacher_name")

            # відправляємо дані до БД
            await db.verification.add_verif_teacher(user_id, teacher_name)

            await callback.message.answer(
                "✅ <b>Успішно</b>\n\n"
                f"Доступ для <code>{teacher_name}</code> "
                f"(ID: <code>{user_id}</code>) додано до системи.",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await callback.message.answer(
                "❌ <b>Помилка при збереженні</b>\n\n"
                "Спробуйте пізніше або зверніться до адміністратора.",
                parse_mode=ParseMode.HTML
            )
            self.log.error(f"Error devmode/access/add: {e}")
        finally:
            await state.clear()

    @staticmethod
    async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
        """Обробка callback скасування операції"""
        await callback.answer()
        await state.clear()

        await callback.message.answer(
            "🔄 <b>Скасовано</b>\n\n"
            "Введіть дані знову у форматі:\n\n"
            "<code>user_id</code>\n"
            "<code>teacher_name</code>",
            parse_mode=ParseMode.HTML
        )

        # повертаємось до стану очікування даних
        await state.set_state(DevAddAccess.waiting_for_data)
