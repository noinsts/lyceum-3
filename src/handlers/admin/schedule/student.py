# TODO: зробить рефакторинг, винести деяку логіку

from typing import Set, List, Tuple

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import SubmitKeyboard, SelectForm
from src.utils import classes
from src.states.admin import StudentSchedule
from src.db.connector import DBConnector
from src.service import broadcast
from src.filters.callbacks import FormsListCallback

HANDLER_TRIGGER = "change_schedule_student"
FINISH_TRIGGER = "selected_forms_done"
SELECTED_FORMS_TRIGGER = "selected_forms_list"
SUBMIT_TRIGGER = "submit_send_student_schedule_broadcast"
CANCEL_TRIGGER = "cancel_send_student_schedule_broadcast"


class StudentsChangeSchedule(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == HANDLER_TRIGGER
        )

        self.router.callback_query.register(
            self.final,
            F.data == FINISH_TRIGGER,
            StudentSchedule.waiting_for_forms
        )

        self.router.callback_query.register(
            self.selected_forms,
            F.data == SELECTED_FORMS_TRIGGER,
            StudentSchedule.waiting_for_forms
        )

        self.router.callback_query.register(
            self.input_form,
            FormsListCallback.filter(),
            StudentSchedule.waiting_for_forms
        )

        self.router.callback_query.register(
            self.confirm,
            F.data == SUBMIT_TRIGGER,
            StudentSchedule.waiting_for_confirmation
        )

        self.router.callback_query.register(
            self.cancel,
            F.data == CANCEL_TRIGGER,
            StudentSchedule.waiting_for_confirmation
        )

    @staticmethod
    async def handler(callback: CallbackQuery, state: FSMContext) -> None:
        forms = classes.CLASSES

        await callback.message.answer(
            "Оберіть класи зі списку",
            reply_markup=SelectForm().get_keyboard(forms)
        )

        await state.set_state(StudentSchedule.waiting_for_forms)

        dataset = set()
        await state.update_data(dataset=list(dataset))
        await state.update_data(forms=forms)

        # заглушка
        await callback.answer()

    async def input_form(self, callback: CallbackQuery, callback_data: FormsListCallback, state: FSMContext) -> None:
        data = await state.get_data()

        forms = data.get("forms")
        dataset = set(data.get("dataset", []))

        valid, response, updated_dataset = self._validate_forms(callback_data.form, dataset, forms)

        if valid:
            await state.update_data(dataset=list(updated_dataset))

        await callback.answer(response)

    # TODO: винести в validators

    @staticmethod
    def _validate_forms(raw: str, dataset: Set[str], forms: List[str]) -> Tuple[bool, str, Set[str]]:
        """
        Метод валідує введений клас та оновлює множину обраних класів.

        Args:
            raw (str): Введений користувачем клас.
            dataset (Set[str]): Набір уже обраних класів.
            forms (List[str]): Список доступних для вибору класів.

        Returns:
            Tuple:
                bool: Чи валідне введення.
                str: Повідомлення для користувача.
                Set[str]: Оновлений набір обраних класів.
        """
        if raw not in forms:
            return False, "❌ Такого класу не існує", dataset

        if raw in dataset:
            dataset.remove(raw)
            return True, f"Ви видалили {raw} з списку класів.", dataset

        dataset.add(raw)
        return True, f"Ви додали {raw} до списку класів", dataset

    async def selected_forms(self, callback: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        forms = set(data.get("dataset", []))

        if not forms:
            await callback.answer(
                "Ви поки що не обрали жодного класу, але ще не пізно це виправить..."
            )
            return

        prompt = "<b>Список обраних класів</b>\n\n"
        prompt += self._forms_prompt(forms)

        await callback.message.edit_text(prompt, parse_mode=ParseMode.HTML)
        await callback.answer()

    async def final(self, callback: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        dataset = set(data.get("dataset", []))

        if len(dataset) < 1:
            await callback.answer(
                "❌ Ви не вказали жодного класу. "
                "Якщо хочете скасувати відправлення оголошення, то напишіть /cancel"
            )
            return

        prompt = "<b>Ви хочете надіслати сповіщення про зміну розкладу таким класам:</b>\n\n"
        prompt += self._forms_prompt(dataset)
        prompt += "\n<i>оберіть наступну дію</i>"

        await state.set_state(StudentSchedule.waiting_for_confirmation)

        await callback.message.edit_text(
            prompt,
            reply_markup=SubmitKeyboard().get_keyboard(SUBMIT_TRIGGER, CANCEL_TRIGGER),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()

    @staticmethod
    async def confirm(callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        await callback.answer()

        data = await state.get_data()
        dataset = set(data.get("dataset"))

        prompt = (
            "📢 <b>Увага! Зміни в розкладі</b>\n\n"
            "Перегляньте новий розклад."
        )

        total_sent, total_failed = 0, 0

        for form in dataset:
            student_ids = await db.register.get_by_form(form)
            sent, failed = await broadcast(prompt, student_ids)

            total_sent += sent
            total_failed += failed

        await callback.message.edit_text(
            f"✅ Сповіщення надіслано!\n\n"
            f"📨 Успішно: <b>{total_sent}</b>\n"
            f"❌ Не вдалося: <b>{total_failed}</b>",
            parse_mode=ParseMode.HTML
        )

    @staticmethod
    async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()

        await state.update_data(dataset=[])
        await state.set_state(StudentSchedule.waiting_for_forms)

        await callback.message.edit_text(
            "Ну і ладно, введіть класи, які хочете сповістити",
            reply_markup=SelectForm().get_keyboard(classes.CLASSES)
        )

    @staticmethod
    def _forms_prompt(forms: Set[str]) -> str:
        return "".join(f"🔹 {form}\n" for form in forms)
