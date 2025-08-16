from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import TeacherManageForm


class Triggers(str, Enum):
    HANDLER = "👥 Мій клас"


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
            F.text == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, message: Message, state: FSMContext) -> None:
        await state.clear()

        # додати перевірку чи є клас

        await message.answer(
            Messages.HANDLER,
            reply_markup=TeacherManageForm().get_keyboard(),
            parse_mode=ParseMode.HTML
        )
