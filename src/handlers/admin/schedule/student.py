from dataclasses import dataclass
from typing import Set, Callable
from functools import wraps
from enum import Enum

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import SubmitKeyboard, SelectForm, AddingListKeyboard, BackButton
from src.utils import classes
from src.states.admin import StudentSchedule
from src.db.connector import DBConnector
from src.service import broadcast
from src.filters.callbacks import FormsListCallback
from src.exceptions import ValidationError
from src.decorators import next_state


def check_selected_forms():
    """
    Декоратор перевіряє наявність елементів
    в списку доданих класів
    """
    def decorator(handler_func: Callable):
        @wraps(handler_func)
        async def wrapper(self, event: CallbackQuery, state: FSMContext, *args, **kwargs):
            forms = set((await state.get_data()).get("selected_forms", []))

            if not forms:
                await event.answer(Messages.NOT_SELECTED_FORMS, show_alert=True)
                raise ValidationError

            await handler_func(self, event, state, forms=forms, *args, **kwargs)
        return wrapper
    return decorator


class Triggers(str, Enum):
    HUB = "admin_schedule_hub"
    HANDLER = "admin_schedule_student"
    LIST = "selected_forms_list"
    CONFIRMATION = "selected_forms_done"
    SUBMIT = "admin_schedule_student_submit"


@dataclass(frozen=True)
class Messages:
    SELECT_FORMS: str = (
        "Оберіть класи зі списку"
    )

    NOT_SELECTED_FORMS: str = (
        "❌ Ви не вказали жодного класу. "
        "Якщо хочете скасувати відправлення оголошення, то напишіть /cancel"
    )

    CONFIRMATION_TITLE: str = (
        "<b>Ви хочете надіслати сповіщення про зміну розкладу таким класам:</b>\n\n"
    )

    SELECT_NEXT_ACTION: str = (
        "\n<i>оберіть наступну дію</i>"
    )

    FORMS_LIST_TITLE: str = (
        "<b>Список обраних класів</b>\n\n"
    )

    SEND_PROMPT: str = (
        "📢 <b>Увага! Зміни в розкладі</b>\n\n"
        "Перегляньте новий розклад."
    )

    SUBMIT: str = (
        "✅ Сповіщення надіслано!\n\n"
        "📨 Успішно: <b>{total_sent}</b>\n"
        "❌ Не вдалося: <b>{total_failed}</b>"
    )


class StudentsChangeSchedule(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.callback_query.register(
            self.get_form,
            FormsListCallback.filter(),
            StudentSchedule.waiting_for_forms
        )

        self.router.callback_query.register(
            self.selected_forms,
            F.data == Triggers.LIST,
            StudentSchedule.waiting_for_forms
        )

        self.router.callback_query.register(
            self.show_confirmation,
            F.data == Triggers.CONFIRMATION,
            StudentSchedule.waiting_for_forms
        )

        self.router.callback_query.register(
            self.submit,
            F.data == Triggers.SUBMIT,
            StudentSchedule.waiting_for_confirmation
        )

    @classmethod
    @next_state(StudentSchedule.waiting_for_forms)
    async def handler(cls, callback: CallbackQuery, state: FSMContext) -> None:
        forms = classes.CLASSES

        await callback.message.edit_text(
            Messages.SELECT_FORMS,
            reply_markup=SelectForm().get_keyboard(forms, True, Triggers.HUB)
        )

    @classmethod
    async def get_form(cls, callback: CallbackQuery, state: FSMContext, callback_data: FormsListCallback) -> None:
        data = await state.get_data()
        selected_forms = set(data.get("selected_forms", []))
        form =  callback_data.form

        if form in selected_forms:
            selected_forms.remove(form)
            action = "видалено"
        else:
            selected_forms.add(form)
            action = "додано"

        await state.update_data(selected_forms=list(selected_forms))
        await callback.answer(f"{form}: {action}")

    @check_selected_forms()
    async def selected_forms(self, callback: CallbackQuery, state: FSMContext, forms: Set[str]) -> None:
        prompt = Messages.FORMS_LIST_TITLE
        prompt += self.format_forms_list(forms)

        await callback.message.edit_text(
            prompt,
            reply_markup=AddingListKeyboard().get_keyboard(Triggers.HANDLER, Triggers.CONFIRMATION),
            parse_mode=ParseMode.HTML
        )

    @check_selected_forms()
    @next_state(StudentSchedule.waiting_for_confirmation)
    async def show_confirmation(self, callback: CallbackQuery, state: FSMContext, forms: Set[str]) -> None:
        prompt = [
            Messages.CONFIRMATION_TITLE,
            self.format_forms_list(forms),
            Messages.SELECT_NEXT_ACTION,
        ]

        await callback.message.edit_text(
            "\n".join(prompt),
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.HUB),
            parse_mode=ParseMode.HTML
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()

        try:
            selected_forms = set(data.get("selected_forms"))
            total_sent, total_failed = 0, 0

            for form in selected_forms:
                student_ids = await db.register.get_by_form(form)
                sent, failed = await broadcast(Messages.SEND_PROMPT, student_ids)

                total_sent += sent
                total_failed += failed

            await callback.message.edit_text(
                Messages.SUBMIT.format(
                    total_sent=total_sent,
                    total_failed=total_failed
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=BackButton().get_keyboard(Triggers.HUB)
            )

        except Exception as e:
            await callback.answer(f"Виникла помилка: {e}", show_alert=True)
            self.log.error(f"Помилка під час відправки сповіщення про зміну розкладу (учні): {e}", exc_info=True)

    @staticmethod
    def format_forms_list(forms: Set[str]) -> str:
        return "".join(f"🔹 {form}\n" for form in forms)
