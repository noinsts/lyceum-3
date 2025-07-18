import re
from typing import List
from datetime import datetime

from aiogram import F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from ...base import BaseHandler
from src.utils import parse_hub_keyboard
from src.utils.states import CreateOlympStates
from src.keyboards.reply import SkipButton, OlympStages, GetClass
from src.keyboards.inline import SubmitKeyboard
from src.responses import TeacherVerify
from src.db.connector import DBConnector
from src.db.schemas import AddOlymp


class CreateHandler(BaseHandler):
    # Константи для валідації
    DATE_PATTERN = r'^\d{2}-\d{2}-\d{4}$'
    SKIP_BUTTON_TEXT = "🚫 Пропустити"

    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'create_new_olymp'
        )

        self.router.message.register(
            self.subject,
            CreateOlympStates.waiting_for_subject
        )

        self.router.message.register(
            self.form,
            CreateOlympStates.waiting_for_form
        )

        self.router.message.register(
            self.student_name,
            CreateOlympStates.waiting_for_student_name
        )

        self.router.message.register(
            self.olymp_stage,
            CreateOlympStates.waiting_for_olymp_stage
        )

        self.router.message.register(
            self.date,
            CreateOlympStates.waiting_for_date
        )

        self.router.message.register(
            self.note,
            CreateOlympStates.waiting_for_note
        )

        self.router.message.register(
            self.confirm,
            CreateOlympStates.confirm_creating
        )

        self.router.callback_query.register(
            self.submit,
            F.data == 'olymp_submit',
            CreateOlympStates.confirm_creating
        )

        self.router.callback_query.register(
            self.cancel,
            F.data == 'olymp_cancel',
            CreateOlympStates.confirm_creating
        )

    async def handler(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        """Початковий хендлер для створення олімпіади"""
        await callback.answer("")

        # Перевірка верифікації
        teacher_name = await db.register.get_teacher_name(callback.from_user.id)
        verif = await db.verification.is_verif(callback.from_user.id, teacher_name)

        if verif:
            await state.update_data(teacher_name=teacher_name)
            await self._start_olympiad_creation(callback, state)
        else:
            await TeacherVerify.send_msg(callback)

    @staticmethod
    async def _start_olympiad_creation(callback: CallbackQuery, state: FSMContext) -> None:
        """Розпочинає процес створення олімпіади"""
        await state.set_state(CreateOlympStates.waiting_for_subject)
        await callback.message.answer(
            "Оберіть предмет зі списку нижче, <b>поки це не працює, тож просто введіть його</b>",
            parse_mode=ParseMode.HTML
        )

    async def subject(self, message: Message, state: FSMContext) -> None:
        """Оброблює введення предмета"""
        if not self._validate_subject(message.text):
            await message.answer("❌ Будь ласка, введіть коректну назву предмета")
            return

        await state.update_data(subject=message.text.strip())
        await state.set_state(CreateOlympStates.waiting_for_form)

        data = await state.get_data()
        teacher_name = data.get("teacher_name")
        forms = self.sheet.teacher.my_classes(teacher_name)

        # TODO: додати обробку помилок forms на None

        await message.answer(
            "Добре, оберіть клас зі списку нижче",
            reply_markup=GetClass().get_keyboard(forms),
            parse_mode=ParseMode.HTML
        )

    async def form(self, message: Message, state: FSMContext) -> None:
        """Оброблює введення класу"""
        if not self._validate_form(message.text):
            await message.answer("❌ Будь ласка, введіть коректний клас (наприклад: 10-А)")
            return

        # TODO: зробить автоматизовану клавіатуру, через gsheet перевірити які клави є у вчителя
        await state.update_data(form=message.text)
        await state.set_state(CreateOlympStates.waiting_for_student_name)

        await message.answer(
            "Замєчатєльно! Запишіть ПІ всіх учнів через кому.\n"
            "Наприклад: \"Рибалка Поліна, Шостак Андрій, Микитенко Арсен, Лепський Артем\""
        )

    async def student_name(self, message: Message, state: FSMContext) -> None:
        """Оброблює введення імен учнів"""
        students = self._parse_student_names(message.text)

        if not students:
            await message.answer("❌ Будь ласка, введіть імена учнів у правильному форматі")
            return

        await state.update_data(student_name=message.text)
        await state.set_state(CreateOlympStates.waiting_for_olymp_stage)

        await message.answer(
            f"Додано {len(students)} учнів. Оберіть нижче етап олімпіади",
            reply_markup=OlympStages().get_keyboard()
        )

    @staticmethod
    async def olymp_stage(message: Message, state: FSMContext) -> None:
        """Оброблює вибір етапу олімпіади"""
        await state.update_data(olymp_stage=message.text)
        await state.set_state(CreateOlympStates.waiting_for_date)

        await message.answer(
            "Введіть дату проведення олімпіади в форматі \"ДД-ММ-РРРР\" (наприклад: 20-05-2025)",
            reply_markup=ReplyKeyboardRemove()
        )

    async def date(self, message: Message, state: FSMContext) -> None:
        """Оброблює введення дати"""
        if not self._validate_date(message.text):
            await message.answer(
                "❌ Некоректний формат дати. Використовуйте формат ДД-ММ-РРРР (наприклад: 20-05-2025)"
            )
            return

        date = self._parse_date(message.text)

        await state.update_data(date=date)
        await state.set_state(CreateOlympStates.waiting_for_note)

        await message.answer(
            "Додайте коментар, який буде видно всім учням, яких ви запросили на олімпіаду, "
            "якщо не хочете нічого додавати, то натисніть на кнопку нижче",
            reply_markup=SkipButton().get_keyboard()
        )

    async def note(self, message: Message, state: FSMContext) -> None:
        """Оброблює введення примітки"""
        note = None if message.text == self.SKIP_BUTTON_TEXT else message.text.strip()

        await state.update_data(note=note)
        await state.set_state(CreateOlympStates.confirm_creating)
        await self.confirm(message, state)

    async def confirm(self, message: Message, state: FSMContext) -> None:
        """Показує підтвердження введених даних"""
        data = await state.get_data()

        text = self._format_confirmation_text(data)

        await message.answer(
            text,
            reply_markup=SubmitKeyboard().get_keyboard(
                submit_cb="olymp_submit", cancel_cb="olymp_cancel"
            ),
            parse_mode=ParseMode.HTML
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        await callback.answer("")

        try:
            data = await state.get_data()
            await self._create_olympiad(data, db)

            await callback.message.answer(
                "✅ Олімпіаду успішно створено.",
                reply_markup=await parse_hub_keyboard(callback.from_user.id)
            )

        except Exception as e:
            await callback.message.answer(
                "❌ Помилка при створенні олімпіади. Спробуйте знову."
            )
            self.log.error(f"Error creating olympiad: {e}")
        finally:
            await state.clear()

    @staticmethod
    async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
        """Скасовує створенн олімпіади"""
        await callback.answer("")
        await state.set_state(CreateOlympStates.waiting_for_subject)
        await callback.message.answer("Добре, введіть предмет ще раз")

    # Приватні методи для валідації та парсингу

    @staticmethod
    def _validate_subject(subject: str) -> bool:
        """Валідує назву предмета"""
        return bool(subject and subject.strip() and len(subject.strip()) >= 2)

    @staticmethod
    def _validate_form(form: str) -> bool:
        """Валідує клас"""
        return bool(form and form.strip() and len(form.strip()) >= 2)
        # FIXME: замінити методом з register.py

    @staticmethod
    def _parse_student_names(names_str: str) -> List[str]:
        if not names_str:
            return []

        names = [name.strip() for name in names_str.split(',')]
        return [name for name in names if name and len(name) >= 2]

    def _validate_date(self, date_str: str) -> bool:
        if not re.match(self.DATE_PATTERN, date_str):
            return False

        try:
            day, month, year = map(int, date_str.split('-'))
            datetime(year, month, day)
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_date(date_str: str) -> datetime.strptime:
        return datetime.strptime(date_str, "%d-%m-%Y").date()

    @staticmethod
    def _format_confirmation_text(data: dict) -> str:
        """Форматує текст підтвердження"""
        return (
            f"📋 <b>Перевірка введених даних:</b>\n\n"
            f"📚 <b>Предмет:</b> {data.get('subject')}\n"
            f"🏫 <b>Клас:</b> {data.get('form')}\n"
            f"👥 <b>Учасники:</b> {data.get('student_name')}\n"
            f"🏆 <b>Етап олімпіади:</b> {data.get('olymp_stage')}\n"
            f"📅 <b>Дата:</b> {data.get('date')}\n"
            f"📝 <b>Примітка:</b> {data.get('note') or '—'}\n\n"
            f"<i>все вірно?</i>"
        )

    @staticmethod
    async def _create_olympiad(data: dict, db: DBConnector) -> None:
        """Створення олімпіади в базі даних"""
        form = data.get("form")
        student_names = data.get("student_name").split(", ")
        teacher_name = data.get("teacher_name")
        subject = data.get("subject")
        stage_olymp = data.get("olymp_stage")
        date = data.get("date")
        note = data.get("note")

        for student in student_names:
            await db.olymp.add_member(
                AddOlymp(
                    form=form,
                    student_name=student,
                    teacher_name=teacher_name,
                    subject=subject,
                    stage_olymp=stage_olymp,
                    date=date,
                    note=note
                )
            )
