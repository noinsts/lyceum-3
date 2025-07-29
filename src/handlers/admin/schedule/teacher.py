from typing import List, Set, Optional, Tuple

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from db.connector import DBConnector
from ...base import BaseHandler
from src.states.admin import TeacherSchedule
from src.keyboards.inline import TeacherTypes, TeacherList, AdminTeacherBackToCategory, SubmitKeyboard
from src.filters.callbacks import TeacherCategoryCallback, TeacherListCallback
from src.enums import TeacherTypeEnum
from src.service import broadcast
from src.utils import JSONLoader

HANDLER_TRIGGER = "change_schedule_teacher"
BACK_TRIGGGER = "admin_back_to_select_category"
DONE_TRIGGER = "admin_teacher_schedule_done"
LIST_TRIGGER = "admin_teacher_schedule_list"
SUBMIT_TRIGGER = "submit_admin_schedule_teacher"
CANCEL_TRIGGER = "cancel_admin_schedule_teacher"


class TeachersChangeSchedule(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == HANDLER_TRIGGER
        )
        self.router.callback_query.register(
            self.get_category,
            TeacherCategoryCallback.filter(),
            TeacherSchedule.waiting_for_category
        )

        self.router.callback_query.register(
            self.get_teacher_name,
            TeacherListCallback.filter(),
            TeacherSchedule.waiting_for_names
        )

        self.router.callback_query.register(
            self.catch_back_button,
            F.data == BACK_TRIGGGER,
            TeacherSchedule.waiting_for_names
        )

        self.router.callback_query.register(
            self.done,
            F.data == DONE_TRIGGER,
            StateFilter(TeacherSchedule.waiting_for_names, TeacherSchedule.waiting_for_category)
        )

        self.router.callback_query.register(
            self.show_list,
            F.data == LIST_TRIGGER,
            TeacherSchedule.waiting_for_category
        )

        self.router.callback_query.register(
            self.submit,
            F.data == SUBMIT_TRIGGER,
            TeacherSchedule.waiting_for_confirmation
        )

        self.router.callback_query.register(
            self.cancel,
            F.data == CANCEL_TRIGGER,
            TeacherSchedule.waiting_for_confirmation
        )

    @staticmethod
    async def handler(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(TeacherSchedule.waiting_for_category)

        await callback.message.answer(
            "Нижче оберіть категорію вчителя.",
            reply_markup=TeacherTypes().get_keyboard()
        )

        # заглушка
        await callback.answer()

    @staticmethod
    async def get_category(
            callback: CallbackQuery,
            callback_data: TeacherCategoryCallback,
            state: FSMContext,
            db: DBConnector
    ) -> None:
        category = TeacherTypeEnum[callback_data.name.upper()]

        teachers = await db.qualification.get_by_category(category)

        if not teachers:
            await callback.answer(
                "❌ Помилка. Вчителів не знайдено. Зверніться до розробників.",
                show_alert=True
            )
            return

        await state.set_state(TeacherSchedule.waiting_for_names)

        await callback.message.edit_text(
            f"Ви обрали: {category.value}, тепер оберіть потрібних вчителів",
            reply_markup=TeacherList().get_keyboard(teachers)
        )

    @staticmethod
    async def get_teacher_name(
            callback: CallbackQuery,
            callback_data: TeacherListCallback,
            state: FSMContext
    ) -> None:
        data = await state.get_data()
        dataset = set(data.get("dataset", []))

        teacher_id = callback_data.teacher_id

        added = teacher_id not in dataset
        dataset.add(teacher_id) if added else dataset.remove(teacher_id)
        response = "Додано." if added else "Видалено."

        await state.update_data(dataset=list(dataset))
        await callback.answer(response)

    @staticmethod
    async def catch_back_button(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(TeacherSchedule.waiting_for_category)

        await callback.message.edit_text(
            "Оберіть потрібну категорію.",
            reply_markup=TeacherTypes().get_keyboard()
        )

    async def done(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            db: DBConnector,
            teacher_names: Optional[List[str]] = None
    ) -> None:
        if not teacher_names:
            data = await state.get_data()
            dataset = set(data.get("dataset", []))

            validate, reason = self._validator(dataset)

            if not validate:
                await callback.answer(reason, show_alert=True)
                return

            teacher_names = await self._fetch_teacher_names_by_ids(dataset, db)

        prompt = self._format_teacher_list(teacher_names)

        await state.update_data(teacher_names=teacher_names)
        await state.set_state(TeacherSchedule.waiting_for_confirmation)

        await callback.message.edit_text(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=SubmitKeyboard().get_keyboard(
                submit_cb="submit_admin_schedule_teacher",
                cancel_cb="cancel_admin_schedule_teacher"
            )
        )

    async def show_list(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()
        dataset = set(data.get("dataset", []))

        validate, reason = self._validator(dataset)

        if not validate:
            await callback.answer(reason, show_alert=True)
            return

        teacher_names = await self._fetch_teacher_names_by_ids(dataset, db)

        prompt = self._format_teacher_list(teacher_names)

        await state.set_state(TeacherSchedule.waiting_for_names)

        await callback.message.edit_text(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=AdminTeacherBackToCategory().get_keyboard()
        )

    @staticmethod
    def _validator(dataset: Set[int]) -> Tuple[bool, Optional[str]]:
        """
        Валідує dataset

        Args:
            dataset (Set[int]): множина з ID вчителів

        Returns:
            Tuple:
                bool: чи проходить валідація
                Optional[str]: причина фейлу валідації
        """
        if not dataset:
            return False, "❌ Помилка. Ви ще не додали жодного вчителя."
        return True, ""

    @staticmethod
    async def _fetch_teacher_names_by_ids(dataset: Set[int], db: DBConnector) -> List[str]:
        """
        Метод повертає список імен вчителів з бд

        Args:
            dataset (Set[int]): список ID вчителів
            db (DBConnector): БД з вчителями

        Returns:
            List[str]: масив імен вчителів за ID
        """
        return [
            await db.qualification.get_teacher_by_id(tid) for tid in dataset
        ]

    @staticmethod
    def _format_teacher_list(teacher_names: List[str]) -> str:
        prompt = "<b>Ви додали таких вчителів:</b>\n\n"
        return prompt + "\n".join(f"🔹 {name}" for name in teacher_names)

    @staticmethod
    async def submit(callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()
        teacher_names = data.get("teacher_names")

        total_sent, total_failed = 0, 0

        vocative_teacher_names = JSONLoader("settings/vocative_teacher_shortname.json")

        for teacher_name in teacher_names:
            user_ids = await db.register.get_by_teacher_name(teacher_name)

            if not user_ids:
                continue

            # Відрізати 2 останніх слова: ['Ім'я', 'По-батькові']
            short_name_parts = teacher_name.split(" ")[-2:]
            short_name = " ".join(short_name_parts)  # Збираємо назад рядок

            vocative_name = vocative_teacher_names.get(short_name)

            if vocative_name:
                teacher_name = vocative_name

            prompt = (
                f"<b>Шановний(-а), {teacher_name}</b>\n\n"
                "📌 Перегляньте ваш розклад, там є зміни.."
            )

            send, failed = await broadcast(prompt, user_ids)

            total_sent += send
            total_failed += failed

        await state.clear()

        await callback.message.edit_text(
            f"✅ Сповіщення надіслано!\n\n"
            f"📨 Успішно: <b>{total_sent}</b>\n"
            f"❌ Не вдалося: <b>{total_failed}</b>",
            parse_mode=ParseMode.HTML
        )

    @staticmethod
    async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await state.set_state(TeacherSchedule.waiting_for_category)

        await callback.message.edit_text(
            "Добре, оберіть потрібну категорію.",
            reply_markup=TeacherTypes().get_keyboard()
        )
