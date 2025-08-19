from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import CardHub


class Triggers(str, Enum):
    MESSAGE = "🃏 Колекції (demo)"
    CALLBACK = "card_hub"


@dataclass(frozen=True)
class Messages:
    HUB: str = (
        "🃏 <b>Колекції</b>\n\n"
        "Тут ви можете збирати колекційні картки з вчителями та "
        "іншими різними цікавими персонажами Березанського ліцей №3.\n"
        "Кожна картка має свою рідкість: від звичайної до легендарної.\n\n"
        "Раз на тиждень ви маєте змогу отримати одну випадкову картку."
        "Вона зберігається у вашому інвентарі.\n\n"
        "🎯 Спробуйте зібрати повну колекцію та станьте справжнім майстром карток!"
    )


class HubHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.hub,
            F.text == Triggers.MESSAGE
        )

        self.router.callback_query.register(
            self.hub,
            F.data == Triggers.CALLBACK
        )

        # self.router.message.register(
        #     self.get_sticker_id,
        #     F.sticker
        # )

    @classmethod
    async def hub(cls, event: Message | CallbackQuery, state: FSMContext) -> None:
        await state.clear()

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(
                Messages.HUB,
                reply_markup=CardHub().get_keyboard(),
                parse_mode=ParseMode.HTML
            )
        else:
            await event.answer(
                Messages.HUB,
                reply_markup=CardHub().get_keyboard(),
                parse_mode=ParseMode.HTML
            )

    @classmethod
    async def get_sticker_id(cls, message: Message) -> None:
        await message.reply(
            f"<b>Sticker ID</b>: <code>{message.sticker.file_unique_id}</code>",
            parse_mode=ParseMode.HTML
        )
