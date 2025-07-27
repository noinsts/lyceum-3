# TODO: зробить рефакторинг, винести деяку логіку

from typing import Set, List, Tuple

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from ...base import BaseHandler
from src.keyboards.reply import GetClassWithDone
from src.keyboards.inline import SubmitKeyboard
from src.utils import classes
from src.states.admin import StudentSchedule
from src.db.connector import DBConnector
from src.bot_instance import get_bot

FINISH_TRIGGER = "✅ Готово"
SELECTED_FORMS_TRIGGER = "ℹ️ Обрані класи"


class StudentsChangeSchedule(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == 'change_schedule_student'
        )

        self.router.message.register(
            self.final,
            StudentSchedule.waiting_for_forms,
            F.text == FINISH_TRIGGER
        )

        self.router.message.register(
            self.selected_forms,
            StudentSchedule.waiting_for_forms,
            F.text == SELECTED_FORMS_TRIGGER
        )

        self.router.message.register(
            self.input_form,
            StudentSchedule.waiting_for_forms
        )

        self.router.callback_query.register(
            self.confirm,
            StudentSchedule.waiting_for_confirmation,
            F.data == 'submit_send_student_schedule_broadcast'
        )

        self.router.callback_query.register(
            self.cancel,
            StudentSchedule.waiting_for_confirmation,
            F.data == 'cancel_send_student_schedule_broadcast'
        )

    @staticmethod
    async def handler(callback: CallbackQuery, state: FSMContext) -> None:
        markup = GetClassWithDone().get_keyboard(classes.CLASSES)

        await callback.message.answer(
            "Оберіть класи зі списку",
            reply_markup=markup
        )

        await state.set_state(StudentSchedule.waiting_for_forms)

        forms = [button.text for row in markup.keyboard for button in row]
        await state.update_data(forms=forms)

        dataset = set()
        await state.update_data(dataset=list(dataset))

        # заглушка
        await callback.answer()

    async def input_form(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()

        forms = data.get("forms")
        dataset = set(data.get("dataset", []))

        valid, response, updated_dataset = self._validate_forms(message.text, dataset, forms)

        if valid:
            await state.update_data(dataset=list(updated_dataset))

        await message.answer(
            response,
            parse_mode=ParseMode.HTML
        )

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
        if raw in forms:
            return False, "❌ Такого класу не існує", dataset

        if raw not in dataset:
            dataset.remove(raw)
            return True, f"Ви видалили <b>{raw}</b> з списку класів.", dataset

        dataset.add(raw)
        return True, f"Ви додали <b>{raw}</b> до списку класів", dataset

    async def selected_forms(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        forms = set(data.get("dataset", []))

        if not forms:
            await message.answer(
                "Ви поки що не обрали жодного класу, але ще не пізно це виправить..."
            )
            return

        prompt = "<b>Список обраних класів</b>\n\n"
        prompt += self._forms_prompt(forms)

        await message.answer(prompt, parse_mode=ParseMode.HTML)

    async def final(self, message: Message, state: FSMContext) -> None:
        await state.set_state(StudentSchedule.waiting_for_confirmation)

        data = await state.get_data()
        dataset = set(data.get("dataset", []))

        if len(dataset) < 1:
            await message.answer(
                "❌ Ви не вказали жодного класу. "
                "Якщо хочете скасувати відправлення оголошення, то напишіть /cancel"
            )
            return

        prompt = "<b>Ви хочете надіслати сповіщення про зміну розкладу таким класам:</b>\n\n"
        prompt += self._forms_prompt(dataset)
        prompt += "\n<i>оберіть наступну дію</i>"

        await message.answer(
            prompt,
            reply_markup=SubmitKeyboard().get_keyboard(
                "submit_send_student_schedule_broadcast",
                "cancel_send_student_schedule_broadcast"
            ),
            parse_mode=ParseMode.HTML
        )

    async def confirm(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        await callback.answer()

        data = await state.get_data()
        dataset = set(data.get("dataset"))

        prompt = (
            "📢 <b>Увага! Зміни в розкладі</b>\n\n"
            "Перегляньте новий розклад."
        )

        count, failed = 0, 0

        for form in dataset:
            student_ids = await db.register.get_by_form(form)
            cc, ff = await self._broadcast_message(prompt, student_ids)

            count += cc
            failed += ff

        await callback.message.answer(
            f"Чудово! Ви надіслали {count}/{failed} учням сповіщення про зміну уроків"
        )

    @staticmethod
    async def _broadcast_message(prompt: str, student_ids: List) -> Tuple:
        """
        Метод оброблює відправку оголошення.

        Args:
            prompt (str): повідомлення, що треба відправити
            student_ids (List[int]): список користувачів, котрим треба відправити сповіщення

        Returns:
            Tuple:
                int: кількість користувачів, які отримали повідомлення
                int: кількість користувачів, що не змогли отримати повідомлення
        """
        bot = get_bot()

        count, failed = 0, 0

        for student_in in student_ids:
            try:
                await bot.send_message(
                    student_in,
                    prompt,
                    parse_mode=ParseMode.HTML
                )
                count += 1
            except (TelegramBadRequest, TelegramForbiddenError):
                failed += 1
                continue

        return count, failed

    @staticmethod
    async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()

        await state.update_data(dataset=[])
        await state.set_state(StudentSchedule.waiting_for_forms)

        await callback.message.answer(
            "Ну і ладно, введіть класи, які хочете сповістити",
            reply_markup=GetClassWithDone().get_keyboard(classes.CLASSES)
        )

    @staticmethod
    def _forms_prompt(forms: Set[str]) -> str:
        return "".join(f"🔹 {form}\n" for form in forms)
