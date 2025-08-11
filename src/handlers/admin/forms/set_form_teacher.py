from aiogram import F
from aiogram.types import CallbackQuery

from ...base import BaseHandler


class SetFormTeacherHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == "set_form_teacher"
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery) -> None:
        await callback.answer(
            "👷🏻 Цей розділ знаходиться в розробці.",
            show_alert=True
        )
