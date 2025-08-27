from typing import List, Set, Optional, Tuple, Callable
from dataclasses import dataclass
from functools import wraps
from enum import Enum

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.db.connector import DBConnector
from src.states.admin import TeacherSchedule
from src.keyboards.inline import TeacherTypes, TeacherList, AddingListKeyboard, SubmitKeyboard, BackButton
from src.filters.callbacks import TeacherCategoryCallback, TeacherListCallback
from src.enums import TeacherTypeEnum
from src.service import broadcast
from src.utils import JSONLoader
from src.decorators import next_state
from src.exceptions import ValidationError


def check_selected_forms():
    """
    Перевіряє наявність обраних вчителів
    """
    def decorator(handler_func: Callable):
        @wraps(handler_func)
        async def wrapper(self, event: CallbackQuery, state: FSMContext, *args, **kwargs):
            selected_teachers = set((await state.get_data()).get("selected_teacher_ids", []))

            if not selected_teachers:
                await event.answer(Messages.NOT_SELECTED_TEACHER, show_alert=True)
                raise ValidationError

            await handler_func(self, event, state, teachers=selected_teachers, *args, **kwargs)
        return wrapper
    return decorator


class Triggers(str, Enum):
    HUB = "admin_schedule_hub"
    HANDLER = "admin_schedule_teacher"
    SUBMIT = "admin_schedule_teacher_submit"

    DONE = "selected_teacher_done"
    LIST = "selected_teacher_list"


@dataclass(frozen=True)
class Messages:
    SELECT_CATEGORY: str = (
        "Нижче оберіть категорію вчителя"
    )

    SELECT_NAME: str = (
        "Ви обрали: {category}, тепер оберіть потрібних вчителів"
    )

    NOT_FOUND_TEACHERS: str = (
        "❌ Помилка. Вчителів не знайдено. Зверніться до розробників."
    )

    NOT_SELECTED_TEACHER: str = (
        "❌ Помилка. Ви ще не додали жодного вчителя."
    )

    TEACHER_LIST_TITLE: str = (
        "<b>Ви додали таких вчителів:</b>\n\n"
    )

    PROMPT_TO_SEND: str = (
        "<b>Шановний(-а), {teacher_name}</b>\n\n"
        "📌 Перегляньте ваш розклад, там є зміни.."
    )

    SENDING_ERROR: str = (
        "❌ Помилка під час відправки сповіщень, спробуйте знову"
    )

    SUBMIT: str = (
        "✅ Сповіщення надіслано!\n\n"
        "📨 Успішно: <b>{total_sent}</b>\n"
        "❌ Не вдалося: <b>{total_failed}</b>"
    )


class TeachersChangeSchedule(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
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
            self.done,
            F.data == Triggers.DONE,
            StateFilter(TeacherSchedule.waiting_for_names, TeacherSchedule.waiting_for_category)
        )

        self.router.callback_query.register(
            self.show_list,
            F.data == Triggers.LIST,
            TeacherSchedule.waiting_for_category
        )

        self.router.callback_query.register(
            self.submit,
            F.data == Triggers.SUBMIT,
            StateFilter(TeacherSchedule.waiting_for_confirmation, TeacherSchedule.waiting_for_names)
        )

    @classmethod
    @next_state(TeacherSchedule.waiting_for_category)
    async def handler(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.SELECT_CATEGORY,
            reply_markup=TeacherTypes().get_keyboard(True, Triggers.HUB)
        )

    @classmethod
    @next_state(TeacherSchedule.waiting_for_names)
    async def get_category(
            cls,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: TeacherCategoryCallback,
            db: DBConnector
    ) -> None:
        category = TeacherTypeEnum[callback_data.name.upper()]
        teachers = await db.qualification.get_by_category(category)

        if not teachers:
            await callback.answer(Messages.NOT_FOUND_TEACHERS, show_alert=True)
            raise ValidationError

        await callback.message.edit_text(
            Messages.SELECT_NAME.format(category=category.value),
            reply_markup=TeacherList().get_keyboard(teachers, Triggers.HANDLER)
        )

    @classmethod
    async def get_teacher_name(
            cls,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: TeacherListCallback
    ) -> None:
        data = await state.get_data()
        selected_teacher_ids = set(data.get("selected_teacher_ids", []))

        teacher_id = callback_data.teacher_id

        added = teacher_id not in selected_teacher_ids
        selected_teacher_ids.add(teacher_id) if added else selected_teacher_ids.remove(teacher_id)
        response = "Додано." if added else "Видалено."

        await state.update_data(selected_teacher_ids=list(selected_teacher_ids))
        await callback.answer(response)

    @check_selected_forms()
    @next_state(TeacherSchedule.waiting_for_confirmation)
    async def done(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            teachers: Set[int],
            db: DBConnector
    ) -> None:
        teacher_names = await self._fetch_teacher_names_by_ids(teachers, db)
        prompt = self._format_teacher_list(teacher_names)

        await state.update_data(teacher_names=teacher_names)

        await callback.message.edit_text(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.HUB)
        )

    @check_selected_forms()
    @next_state(TeacherSchedule.waiting_for_names)
    async def show_list(self, callback: CallbackQuery, state: FSMContext, teachers: Set[int], db: DBConnector) -> None:
        teacher_names = await self._fetch_teacher_names_by_ids(teachers, db)
        prompt = self._format_teacher_list(teacher_names)

        await state.update_data(teacher_names=teacher_names)

        await callback.message.edit_text(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=AddingListKeyboard().get_keyboard(Triggers.HANDLER, Triggers.SUBMIT)
        )

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
        prompt = Messages.TEACHER_LIST_TITLE
        return prompt + "\n".join(f"🔹 {name}" for name in teacher_names)

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()

        try:
            teacher_names = data.get("teacher_names")
            total_sent, total_failed = 0, 0
            json = JSONLoader("settings/vocative_teacher_shortname.json")

            for teacher_name in teacher_names:
                user_ids = await db.register.get_by_teacher_name(teacher_name)
                if not user_ids:
                    continue

                vocative = self._get_vocative(teacher_name, json)
                teacher_name = vocative if vocative else teacher_name

                prompt = Messages.PROMPT_TO_SEND.format(teacher_name=teacher_name)
                send, failed = await broadcast(prompt, user_ids)

                total_sent += send
                total_failed += failed

            await callback.message.edit_text(
                Messages.SUBMIT.format(
                    total_sent=total_sent,
                    total_failed=total_failed
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=BackButton().get_keyboard(Triggers.HUB)
            )

            await state.clear()

        except Exception as e:
            await callback.answer(Messages.SENDING_ERROR, show_alert=True)
            self.log.error(f"Помилка під час відправки оголошення про зміну розкладу: {e}", exc_info=True)


    @staticmethod
    def _get_vocative(teacher_name: str, json: JSONLoader) -> Optional[str]:
        short_name_parts = teacher_name.split(" ")[-2:]
        short_name = " ".join(short_name_parts)
        vocative_name = json.get(short_name)
        return vocative_name
