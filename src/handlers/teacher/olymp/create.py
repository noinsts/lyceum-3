import re
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import date

from aiogram import F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from ...base import BaseHandler
from src.utils import parse_hub_keyboard
from src.states import CreateOlympStates
from src.keyboards.reply import SkipButton, OlympStages, GetClass, UniversalKeyboard
from src.keyboards.inline import SubmitKeyboard
from src.handlers.service.teacher_verify import TeacherVerifyHandler
from src.db.connector import DBConnector
from src.db.schemas import AddOlymp
from src.validators import validate_date, validate_form, validate_student_name
from src.parsers.frontend import parse_date
from src.decorators import with_validation, next_state
from src.enums import OlympStage
from src.exceptions import ValidationError


# =====================
# Константи та Enum-и
# =====================


class Triggers(str, Enum):
    HANDLER = "create_new_olymp"
    SUBMIT = "create_olymp_submit"
    CANCEL = "create_olymp_cancel"


@dataclass(frozen=True)
class Messages:
    SELECT_SUBJECT: str = (
        "Оберіть потрібний предмет зі списку нижче"
    )

    INPUT_SUBJECT: str = (
        "Введіть предмет, з якого буде проводитись олімпіада"
    )

    SUBJECT_ERROR: str = (
        "❌ Такого предмету не існує, спробуйте знову"
    )

    SELECT_FORM: str = (
        "Добре, оберіть клас зі списку"
    )

    INPUT_FORM: str = (
        "Введіть клас в форматі \"8-А\""
    )

    FORM_ERROR: str = (
        "❌ Такого класу не існує, спробуйте знову"
    )

    INPUT_STUDENT_NAMES: str = (
        "Замєчатєльно! Запишіть ПІ всіх учнів через кому.\n"
        "Наприклад: \"Рибалка Поліна, Шостак Андрій, Микитенко Арсен, Лепський Артем\""
    )

    STUDENT_NAME_VALIDATION_ERROR: str = (
        "❌ Будь ласка, введіть імена учнів у правильному форматі"
    )

    INPUT_OLYMP_STAGE: str = (
        "Додано {count} учнів. Оберіть нижче етап олімпіади"
    )

    OLYMP_STAGE_EXCEPTION: str = (
        "❌ Вкажіть вірний етап олімпіади."
    )

    INPUT_DATE: str = (
        "Введіть дату проведення олімпіади в форматі \"ДД-ММ-РРРР\" (наприклад: 20-05-2025)"
    )

    INPUT_NOTE: str = (
        "Додайте коментар, який буде видно всім учням, яких ви запросили на олімпіаду, "
        "якщо не хочете нічого додавати, то натисніть на кнопку нижче"
    )

    SKIP_BUTTON_TEXT = (
        "🚫 Пропустити"
    )

    CONFIRMATION_TEXT: str = (
        "📋 <b>Перевірка введених даних:</b>\n\n"
        "📚 <b>Предмет:</b> {subject}\n"
        "🏫 <b>Клас:</b> {form}\n"
        "👥 <b>Учасники:</b> {student_names}\n"
        "🏆 <b>Етап олімпіади:</b> {olymp_stage}\n"
        "📅 <b>Дата:</b> {date}\n"
        "📝 <b>Примітка:</b> {note}\n\n"
        "<i>все вірно?</i>"
    )

    SUCCESS: str = (
        "✅ Олімпіаду успішно створено."
    )

    CREATE_OLYMP_EXCEPTION: str = (
        "❌ Помилка при створенні олімпіади. Спробуйте знову."
    )

    CANCEL: str = (
        "✖️ Скасовано."
    )


# =================
# Основний клас
# =================


class CreateHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self._register_step_handlers()
        self._register_confirmation_handlers()

    def _register_step_handlers(self) -> None:
        handlers_config = [
            (self.subject, CreateOlympStates.waiting_for_subject),
            (self.form, CreateOlympStates.waiting_for_form),
            (self.student_name, CreateOlympStates.waiting_for_student_name),
            (self.olymp_stage, CreateOlympStates.waiting_for_olymp_stage),
            (self.date, CreateOlympStates.waiting_for_date),
            (self.note, CreateOlympStates.waiting_for_note),
            (self.show_confirmation, CreateOlympStates.confirm_creating)
        ]

        for handler, state in handlers_config:
            self.router.message.register(handler, state)

    def _register_confirmation_handlers(self) -> None:
        self.router.callback_query.register(
            self.submit_olympiad,
            F.data == Triggers.SUBMIT,
            CreateOlympStates.confirm_creating
        )

        self.router.callback_query.register(
            self.cancel_creation,
            F.data == Triggers.CANCEL,
            CreateOlympStates.confirm_creating
        )

    # ===================
    # Кроки форми
    # ===================

    @next_state(CreateOlympStates.waiting_for_subject)
    async def handler(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        """Початок створення олімпіади"""
        await callback.answer()

        teacher_name = await db.register.get_teacher_name(callback.from_user.id)
        is_verified = await db.verification.is_verif(callback.from_user.id, teacher_name)

        if not is_verified:
            await TeacherVerifyHandler().send_msg(callback, "sdgdfjkgdfhgkjfdhgjk")
            # TODO: handlers/teachers/olymp/hub.py callback data
            raise ValidationError

        await state.update_data(teacher_name=teacher_name)

        sheet = await self.get_sheet()
        subject_list = await sheet.teacher.my_forms_or_subjects(teacher_name, "subject")

        if subject_list:
            await callback.message.answer(
                Messages.SELECT_SUBJECT,
                reply_markup=UniversalKeyboard().get_keyboard(subject_list)
            )
            await state.update_data(subject_list=subject_list)
        else:
            await callback.message.answer(Messages.INPUT_SUBJECT, reply_markup=ReplyKeyboardRemove())


    @next_state(CreateOlympStates.waiting_for_form)
    async def subject(self, message: Message, state: FSMContext) -> None:
        """Оброблює введення предмета"""
        subject = message.text.strip()

        data = await state.get_data()
        subject_list = data.get("subject_list")

        if subject_list and subject not in subject_list:
            await message.answer(Messages.SUBJECT_ERROR)
            raise ValidationError

        await state.update_data(subject=subject)

        teacher_name = data.get("teacher_name")

        sheet = await self.get_sheet()
        forms_list = await sheet.teacher.my_forms_or_subjects(teacher_name, "form")

        if forms_list:
            await message.answer(
                Messages.SELECT_FORM,
                reply_markup=GetClass().get_keyboard(forms_list),
                parse_mode=ParseMode.HTML
            )
            await state.update_data(forms_list=forms_list)
        else:
            await message.answer(Messages.INPUT_FORM, reply_markup=ReplyKeyboardRemove())

    @classmethod
    @next_state(CreateOlympStates.waiting_for_student_name)
    @with_validation(validate_form)
    async def form(cls, message: Message, state: FSMContext) -> None:
        """Оброблює введення класу"""
        form = message.text.strip()
        forms_list = (await state.get_data()).get("forms_list")

        if forms_list and form not in forms_list:
            await message.answer(Messages.FORM_ERROR)
            raise ValidationError

        await state.update_data(form=form)
        await message.answer(Messages.INPUT_STUDENT_NAMES, reply_markup=ReplyKeyboardRemove())

    @next_state(CreateOlympStates.waiting_for_olymp_stage)
    async def student_name(self, message: Message, state: FSMContext) -> None:
        """Оброблює введення імен учнів"""
        students = self._parse_and_validate_students(message.text)

        if not students:
            await message.answer(Messages.STUDENT_NAME_VALIDATION_ERROR)
            raise ValidationError

        await state.update_data(student_names=message.text.strip())

        await message.answer(
            Messages.INPUT_OLYMP_STAGE.format(count=len(students)),
            reply_markup=OlympStages().get_keyboard()
        )

    @classmethod
    @next_state(CreateOlympStates.waiting_for_date)
    async def olymp_stage(cls, message: Message, state: FSMContext) -> None:
        """Оброблює вибір етапу олімпіади"""
        try:
            await state.update_data(olymp_stage=OlympStage(message.text).value)
            await message.answer(Messages.INPUT_DATE, reply_markup=ReplyKeyboardRemove())
        except ValueError:
            await message.answer(Messages.OLYMP_STAGE_EXCEPTION)

    @classmethod
    @next_state(CreateOlympStates.waiting_for_note)
    @with_validation(validate_date)
    async def date(cls, message: Message, state: FSMContext) -> None:
        """Оброблює введення дати"""
        await state.update_data(date=parse_date(message.text).isoformat())
        await message.answer(Messages.INPUT_NOTE, reply_markup=SkipButton().get_keyboard())

    @next_state(CreateOlympStates.confirm_creating)
    async def note(self, message: Message, state: FSMContext) -> None:
        """Оброблює введення примітки"""
        note = None if message.text == Messages.SKIP_BUTTON_TEXT else message.text.strip()
        await state.update_data(note=note)
        await self.show_confirmation(message, state)

    async def show_confirmation(self, message: Message, state: FSMContext) -> None:
        """Показує підтвердження введених даних"""
        data = await state.get_data()
        text = self._format_confirmation_text(data)

        await message.answer(
            text,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.CANCEL),
            parse_mode=ParseMode.HTML
        )

    # =================================
    # Підтвердження та створення
    # =================================

    async def submit_olympiad(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        await callback.answer()

        try:
            data = await state.get_data()
            await self._create_olympiad(data, db)

            await callback.message.answer(
                Messages.SUCCESS,
                reply_markup=await parse_hub_keyboard(callback.from_user.id)
            )
        except Exception as e:
            self.log.error(f"Error creating olympiad: {e}", exc_info=True)
            await callback.message.answer(Messages.CREATE_OLYMP_EXCEPTION)
        finally:
            await state.clear()

    @classmethod
    async def cancel_creation(cls, callback: CallbackQuery, state: FSMContext) -> None:
        """Скасовує створенн олімпіади"""
        await state.clear()
        await callback.answer(Messages.CANCEL)

    # ======================
    # Допоміжні методи
    # ======================

    @staticmethod
    def _parse_and_validate_students(text: str) -> Optional[List[str]]:
        students = [n.strip() for n in text.split(",") if n.strip()]
        return students if all(validate_student_name(s) for s in students) else None

    @classmethod
    def _format_confirmation_text(cls, data: dict) -> str:
        """Форматує текст підтвердження"""
        return Messages.CONFIRMATION_TEXT.format(
            subject=data.get("subject"),
            form=data.get("form"),
            student_names=data.get("student_names"),
            olymp_stage=data.get("olymp_stage"),
            date=data.get("date"),
            note=data.get("note") or "—"
        )

    @classmethod
    async def _create_olympiad(cls, data: dict, db: DBConnector) -> None:
        """Створення олімпіади в базі даних"""
        students_str = data.get("student_names", "")
        student_names = re.split(r'\s*,\s*', students_str.strip()) if students_str else []

        olymp_data = {
            'form': data.get("form"),
            'teacher_name': data.get("teacher_name"),
            'subject': data.get("subject"),
            'stage_olymp': data.get("olymp_stage"),
            'date': date.fromisoformat(data.get("date")),
            'note': data.get("note")
        }

        for student_name in student_names:
            await db.olymp.add_member(
                AddOlymp(student_name=student_name, **olymp_data)
            )
