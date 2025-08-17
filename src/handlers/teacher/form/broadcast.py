from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.handlers.service.teacher_verify import TeacherVerifyHandler
from src.db.connector import DBConnector
from src.states.teacher import BroadcastStates
from src.exceptions import ValidationError
from src.decorators import next_state
from src.keyboards.inline import SubmitKeyboard
from src.service import broadcast
from src.keyboards.inline import BackButton


class Triggers(str, Enum):
    HUB = "teacher_my_form_hub"
    HANDLER = "my_form_broadcast"
    SUBMIT = "submit_send_broadcast_my_form"


@dataclass(frozen=True)
class Messages:
    ENTER_A_MESSAGE: str = (
        "Добре, введіть повідомлення, яке ви б хотіли відправити своєму класу"
    )

    CONFIRMATION: str = (
        "<b>Ви хочете надіслати наступне повідомлення учням {form} класу</b>\n\n"
        "💌: {msg}"
    )

    SUBMIT: str = (
        "✅ <b>Повідомлення успішно доставлено!</b>\n\n"
        "Отримали: {send}\n"
        "Не змогли отримати: {failed}"
    )

    ERROR: str = (
        "❌ Сталась помилка під час розсилки, "
        "спробуйте знову, або зверніться до розробників"
    )

    BROADCAST_MESSAGE: str = (
        "📥 <b>Повідомлення від класного керівника</b>\n\n"
        "{msg}"
    )


class BroadcastHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.message.register(
            self.get_message,
            BroadcastStates.waiting_for_message
        )

        self.router.callback_query.register(
            self.submit,
            F.data == Triggers.SUBMIT,
            BroadcastStates.waiting_for_confirmation
        )

    @classmethod
    @next_state(BroadcastStates.waiting_for_message)
    async def handler(cls, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        await state.clear()

        teacher_name = await db.register.get_teacher_name(callback.from_user.id)
        is_verified = await db.verification.is_verif(callback.from_user.id, teacher_name)

        if not is_verified:
            await TeacherVerifyHandler().send_msg(callback, Triggers.HUB)
            raise ValidationError

        teacher_id = await db.verification.get_teacher_id(teacher_name)
        form = await db.form.get_form_by_teacher(teacher_id)

        await state.update_data(form=form)

        await callback.message.edit_text(
            Messages.ENTER_A_MESSAGE,
            reply_markup=BackButton().get_keyboard(Triggers.HUB)
        )

    async def get_message(self, message: Message, state: FSMContext) -> None:
        await state.update_data(msg=message.text)
        await self.send_confirmation(message, state)

    @next_state(BroadcastStates.waiting_for_confirmation)
    async def send_confirmation(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        msg = data.get("msg")
        form = data.get("form")

        await message.answer(
            Messages.CONFIRMATION.format(msg=msg, form=form),
            parse_mode=ParseMode.HTML,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.HUB)
        )

    @classmethod
    async def submit(cls, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()
        msg = Messages.BROADCAST_MESSAGE.format(msg=data.get("msg"))
        form = data.get("form")

        try:
            uids = await db.register.get_by_form(form)
            send, failed = await broadcast(msg, uids)

            await callback.message.edit_text(
                Messages.SUBMIT.format(send=send, failed=failed),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await callback.answer(Messages.ERROR, show_alert=True)
        finally:
            await state.clear()
