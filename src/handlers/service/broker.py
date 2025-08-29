"""
ya ebav multiply
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set
from enum import Enum

import asyncio
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from ..base import BaseHandler
from src.filters.callbacks import (
    BroadcastTypeCallback, BroadcastTypeEnum,
    FormsListCallback, TeacherListCallback, TeacherCategoryCallback
)
from src.keyboards.inline import (
    BroadcastType, SelectFormsMultiply, TeacherTypes, TeacherList,
    BackButton, SubmitKeyboard
)
from src.decorators import next_state
from src.states import BrokerStates
from src.db.connector import DBConnector
from src.exceptions import ValidationError
from src.service import broadcast
from src.enums import TeacherTypeEnum


class Triggers(str, Enum):
    FORM_SHOW = "broker_show_form"
    FORM_DONE = "selected_forms_done"

    TEACHER_SHOW_CATEGORY = "broker_teacher_show_category"
    TEACHER_LIST = "selected_teacher_list"
    TEACHER_DONE = "selected_teacher_done"

    SEND_MESSAGE = "broker_send_message"
    SUBMIT = "submit_broker"


@dataclass(frozen=True)
class Messages:
    HANDLER: str = (
        "Оберіть кому будете надсилати оголошення"
    )

    TRY_AGAIN: str = (
        "Спробуйте знову"
    )

    SELECT_FORM: str = (
        "Нижче оберіть класи, яким треба зробити оголошення"
    )

    NO_FORMS: str = (
        "❌ Помилка, класів не знайдено. Зверніться до розробників."
    )

    NO_SELECTED_FORMS: str = (
        "❌ Ви ще не додали жодного класу, але не пізно це виправити ;)"
    )

    NO_TEACHER_IN_CATEGORY: str = (
        "❌ Cхоже база даних до кінця не заповнена, і вчителів цієї категорії ще не додано... "
        "Спробуйте іншим разом"
    )

    SELECT_TEACHER_CATEGORY: str = (
        "Оберіть потрібну категорію нижче"
    )

    SELECT_TEACHER_NAME: str = (
        "Оберіть потрібних вчителів нижче"
    )

    NO_SELECTED_TEACHERS: str = (
        "❌ Ви ще не додали жодного вчителя, але не пізно це виправити ;)"
    )

    SEND_MESSAGE: str = (
        "Введіть повідомлення, яке хочете відправити"
    )


class BrokerSystemHandler(BaseHandler, ABC):
    def __init__(self):
        self.triggers = self.get_triggers()
        self.signature = self.get_signature()

        super().__init__()

    # =====================================
    # Абстрактні методи для збору даних
    # =====================================

    @abstractmethod
    def get_signature(self) -> Dict[str, str]:
        """
        Повертає дані для footer оголошення

        Returns:
            Dict [str, str]:
                - type: тип admin | developer
                - name: ім'я відправника
        """
        pass

    @abstractmethod
    def get_triggers(self) -> Dict[str, str]:
        """
        Метод повертає словник з тригерами для callback

        Returns:
            Dict:
                hub: тригер повернення до хабу
                handler: тригер початкового хендеру
        """
        pass

    # =========================
    # Реєстрація хендерів
    # =========================

    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == self.triggers['handler']
        )

        self.router.callback_query.register(
            self.get_type,
            BroadcastTypeCallback.filter(),
            BrokerStates.waiting_for_type
        )

        self.router.callback_query.register(
            self.show_forms,
            F.data == Triggers.FORM_SHOW,
            StateFilter(
                BrokerStates.waiting_for_form,
                BrokerStates.waiting_for_continue_form,
                BrokerStates.waiting_for_message
            )
        )

        self.router.callback_query.register(
            self.get_form,
            FormsListCallback.filter(),
            BrokerStates.waiting_for_form
        )

        self.router.callback_query.register(
            self.forms_done,
            F.data == Triggers.FORM_DONE,
            StateFilter(BrokerStates.waiting_for_form, BrokerStates.waiting_for_continue_form)
        )

        self.router.callback_query.register(
            self.show_teacher_category,
            F.data == Triggers.TEACHER_SHOW_CATEGORY,
        )

        self.router.callback_query.register(
            self.get_teacher_category,
            TeacherCategoryCallback.filter(),
            BrokerStates.waiting_for_teacher_category
        )

        self.router.callback_query.register(
            self.teacher_list,
            F.data == Triggers.TEACHER_LIST,
            BrokerStates.waiting_for_teacher_category
        )

        self.router.callback_query.register(
            self.teacher_done,
            F.data == Triggers.TEACHER_DONE,
            BrokerStates.waiting_for_teacher_category
        )

        self.router.callback_query.register(
            self.get_teacher_name,
            TeacherListCallback.filter(),
            BrokerStates.waiting_for_teacher_name
        )

        self.router.callback_query.register(
            self.show_message_feedback,
            F.data == Triggers.SEND_MESSAGE,
            StateFilter(
                BrokerStates.waiting_for_teacher_category,
                BrokerStates.waiting_for_continue_teacher_name,
                BrokerStates.waiting_for_form,
                BrokerStates.waiting_for_continue_form
            )
        )

        self.router.message.register(
            self.get_message,
            BrokerStates.waiting_for_message
        )

        self.router.callback_query.register(
            self.submit,
            F.data == Triggers.SUBMIT,
            BrokerStates.waiting_for_confirmation
        )

    # =========================
    # Загальні методи
    # =========================

    @next_state(BrokerStates.waiting_for_type)
    async def handler(self, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.HANDLER,
            reply_markup=BroadcastType().get_keyboard(self.triggers['hub'])
        )

    async def get_type(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: BroadcastTypeCallback,
            db: DBConnector
    ) -> None:
        method = BroadcastTypeEnum[callback_data.method]
        await state.update_data(method=method)

        match method:
            case BroadcastTypeEnum.ALL:
                await self.show_message_feedback(callback, state)
            case BroadcastTypeEnum.STUDENT:
                await self.show_forms(callback, state, db)
            case BroadcastTypeEnum.TEACHER:
                await self.show_teacher_category(callback, state)

    # =========================
    # Учні
    # =========================

    @next_state(BrokerStates.waiting_for_form)
    async def show_forms(self, callback: CallbackQuery, state: FSMContext, db: DBConnector):
        forms = await db.form.get_all_forms()

        dict_forms: Dict[str, bool] = {item: False for item in forms}

        await state.update_data(forms=dict_forms)

        await callback.message.edit_text(
            Messages.SELECT_FORM,
            reply_markup=SelectFormsMultiply().get_keyboard(self.triggers['handler'], Triggers.FORM_DONE, dict_forms)
        )

    async def get_form(self, callback: CallbackQuery, state: FSMContext, callback_data: FormsListCallback) -> None:
        forms = (await state.get_data()).get("forms")
        form = callback_data.form
        forms[form] = not forms[form]

        await state.update_data(forms=forms)

        await callback.message.edit_reply_markup(
            reply_markup=SelectFormsMultiply().get_keyboard(self.triggers['handler'], Triggers.FORM_DONE, forms)
        )

    async def forms_done(self, callback: CallbackQuery, state: FSMContext) -> None:
        forms = (await state.get_data()).get("forms")
        selected_forms = [k for k, v in forms.items() if v]

        if not selected_forms:
            await callback.answer(Messages.NO_SELECTED_FORMS, show_alert=True)
            raise ValidationError

        await state.update_data(selected_forms=selected_forms)
        await self.show_message_feedback(callback, state)

    # =========================
    # Вчителі
    # =========================

    @next_state(BrokerStates.waiting_for_teacher_category)
    async def show_teacher_category(self, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.SELECT_TEACHER_CATEGORY,
            reply_markup=TeacherTypes().get_keyboard(True, self.triggers['handler'])
        )

    async def get_teacher_category(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: TeacherCategoryCallback,
            db: DBConnector
    ) -> None:
        category = TeacherTypeEnum[callback_data.name.upper()]
        teachers = await db.qualification.get_by_category(category)

        if not teachers:
            await callback.answer(Messages.NO_TEACHER_IN_CATEGORY, show_alert=True)
            return

        await self.show_teacher_name(callback, state, teachers)

    @next_state(BrokerStates.waiting_for_teacher_name)
    async def show_teacher_name(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            teachers: List[Tuple[int, str]]
    ) -> None:
        await callback.message.edit_text(
            Messages.SELECT_TEACHER_NAME,
            reply_markup=TeacherList().get_keyboard(teachers, Triggers.TEACHER_SHOW_CATEGORY)
        )

    async def get_teacher_name(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: TeacherListCallback
    ) -> None:
        selected_teacher_list = set((await state.get_data()).get("selected_teacher_list", []))

        teacher_id = callback_data.teacher_id

        if teacher_id in selected_teacher_list:
            selected_teacher_list.remove(teacher_id)
            response = "Видалено"
        else:
            selected_teacher_list.add(teacher_id)
            response = "Додано"

        await callback.answer(response)
        await state.update_data(selected_teacher_list=list(selected_teacher_list))

    async def teacher_list(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        teacher_list = (await state.get_data()).get("selected_teacher_list")

        try:
            self._validate(teacher_list)
        except ValidationError as e:
            await callback.answer(str(e), show_alert=True)
            return

        prompt = [
            "<b>Список доданих вчителів</b>\n",
            await self._get_pretty_list(teacher_list, db)
        ]

        await callback.message.edit_text(
            "\n".join(prompt),
            reply_markup=BackButton().get_keyboard(Triggers.TEACHER_SHOW_CATEGORY),
            parse_mode=ParseMode.HTML
        )

    async def teacher_done(self, callback: CallbackQuery, state: FSMContext) -> None:
        teacher_list = (await state.get_data()).get("selected_teacher_list")

        try:
            self._validate(teacher_list)
        except ValidationError as e:
            await callback.answer(str(e), show_alert=True)

        await self.show_message_feedback(callback, state)

    # =========================
    # Повідомлення
    # =========================

    @next_state(BrokerStates.waiting_for_message)
    async def show_message_feedback(self, callback: CallbackQuery, state: FSMContext) -> None:
        method = (await state.get_data()).get("method")

        back_callbacks = {
            BroadcastTypeEnum.ALL: self.triggers['handler'],
            BroadcastTypeEnum.STUDENT: Triggers.FORM_SHOW,
            BroadcastTypeEnum.TEACHER: Triggers.TEACHER_SHOW_CATEGORY
        }
        back_callback = back_callbacks.get(method, self.triggers['hub'])

        await callback.message.edit_text(
            Messages.SEND_MESSAGE,
            reply_markup=BackButton().get_keyboard(back_callback)
        )

    async def get_message(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        await state.update_data(message=message.text)
        await self.send_confirmation(message, state, db)

    # =============================
    # Підтвердження та розсилка
    # =============================

    @next_state(BrokerStates.waiting_for_confirmation)
    async def send_confirmation(self, message: Message, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()
        msg = data.get("message")

        method = data.get("method")

        match method:
            case BroadcastTypeEnum.ALL:
                prompt = (
                    "📢 Ви збираєтесь надіслати це повідомлення всій школі.\n\n"
                    f"✉️ Повідомлення:\n{msg}"
                )
            case BroadcastTypeEnum.STUDENT:
                selected_forms = set(data.get("selected_forms"))
                forms_str = ", ".join(sorted(selected_forms))

                prompt = (
                    "🎓 Ви збираєтесь надіслати це повідомлення наступним класам:\n\n"
                    f"{forms_str}\n\n"
                    f"✉️ Повідомлення:\n{msg}"
                )
            case BroadcastTypeEnum.TEACHER:
                selected_teachers = data.get("selected_teacher_list")
                prompt = (
                    "📢 Ви збираєтесь надіслати це повідомлення наступним вчителям:\n\n"
                    f"{await self._get_pretty_list(selected_teachers, db)}"
                )
            case _:
                prompt = "❌ Сталася невідома помилка. Спробуйте ще раз."

        await message.answer(
            prompt,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, self.triggers["hub"])
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()

        method = data.get("method")

        match method:
            case BroadcastTypeEnum.ALL:
                uids = await db.register.get_all_ids()
            case BroadcastTypeEnum.TEACHER:
                teacher_list = data.get("selected_teacher_list", [])

                teacher_names = await asyncio.gather(
                    *(db.verification.get_teacher_name_by_id(tid) for tid in teacher_list)
                )

                teacher_accounts_lists = await asyncio.gather(
                    *(db.register.get_by_teacher_name(name) for name in teacher_names)
                )

                uids = [uid for accounts in teacher_accounts_lists for uid in accounts]
            case BroadcastTypeEnum.STUDENT:
                uids = [
                    uid
                    for form in data.get("selected_forms")
                    for uid in await db.register.get_by_form(form)
                ]
            case _:
                await callback.answer(Messages.TRY_AGAIN, show_alert=True)
                return

        msg = self._format_broadcast_message(data.get("message"), callback.from_user.full_name)

        send, failed = await broadcast(msg, uids)

        await callback.message.edit_text(
            f"✅ Повідомлення успішно доставлено!\n\n"
            f"Отримали: {send}\n"
            f"Не змогли отримати: {failed}",
            parse_mode=ParseMode.HTML
        )

    # =============================
    # Приватні методи
    # =============================

    @staticmethod
    def _validate(teacher_list: Set[int]) -> None:
        if not teacher_list:
            raise ValidationError(Messages.NO_SELECTED_TEACHERS)

    @staticmethod
    async def _get_pretty_list(lst: List[str], db: DBConnector) -> str:
        items = []
        for item in lst:
            name = await db.verification.get_teacher_name_by_id(item)
            items.append(f"🔹 {name}")
        return "\n".join(items)

    def _format_broadcast_message(self, msg: str, name: str) -> str:
        return (
            f"📥 <b>Вам повідомлення</b>\n\n"
            f"{msg}\n\n"
            f"<i>({self.signature['type']}) // <b>{self.signature['name'] or name}</b></i>"
        )
