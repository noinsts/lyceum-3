from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from ..base import BaseHandler


class TeacherVerifyHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.how_get_verify,
            F.data == 'how_get_verify'
        )

    @staticmethod
    async def how_get_verify(callback: CallbackQuery) -> None:
        await callback.answer()  # заглушка
        await callback.message.answer(
            "<b>Як отримати верифікацію?</b>\n\n"
            "Дуже просто! Вам потрібно поставити учню Шостаку Андрію 12 балів з вашого предмету. "
            "Після чого він вас верифікує 😏\n\n"
            "#FIXME: змінити текст",
            parse_mode=ParseMode.HTML
        )

        # FIXME: змінити текст
