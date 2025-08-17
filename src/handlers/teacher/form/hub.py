from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import TeacherManageForm


class Triggers(str, Enum):
    MESSAGE = "👥 Мій клас"
    CALLBACK = "teacher_my_form_hub"


@dataclass(frozen=True)
class Messages:
    HANDLER: str = (
        "👥 <b>Мій клас</b>\n\n"
        "Тут можна керувати своїм класом. "
        "Оберіть, що хочете зробити, за допомогою кнопок нижче."
    )


class HubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            F.text == Triggers.MESSAGE
        )

        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.CALLBACK
        )

    @classmethod
    async def handler(cls, event: Message | CallbackQuery, state: FSMContext) -> None:
        await state.clear()

        # додати перевірку чи є клас

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(
                Messages.HANDLER,
                reply_markup=TeacherManageForm().get_keyboard(),
                parse_mode=ParseMode.HTML
            )
        else:
            await event.answer(
                Messages.HANDLER,
                reply_markup=TeacherManageForm().get_keyboard(),
                parse_mode=ParseMode.HTML
            )
