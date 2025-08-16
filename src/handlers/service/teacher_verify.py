from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.keyboards.inline import TeacherVerifyFAQ, BackButton
from src.filters.callbacks import TeacherVerifyEnum, TeacherVerifyCallback


class Triggers(str, Enum):
    HUB = "teacher_verify_hub"


@dataclass(frozen=True)
class Messages:
    HUB: str = (
        "🚫 Вибачте, ви не можете скористатись цією функцією, оскільки ви не верифікований вчитель"
    )

    HOW_GET: str = (
        "<b>Як отримати верифікацію?</b>\n\n"
        "Напишіть розробнику (Шостаку Андрію, чи як там мене звати) або тому, хто веде цей проєкт. "
        "Після швидкої перевірки вашого статусу (чи справді ви вчитель) — вам дадуть доступ.\n\n"
    )

    WHY_NEED: str = (
        "<b>Навіщо потрібна верифікація?</b>\n\n"
        "🔐 Верифікація потрібна для безпеки. Вона гарантує, що доступ до функцій типу:\n"
        "– створення/редагування олімпіад\n"
        "– дій від імені вчителя\n"
        "має лише справжній педагог, а не умовний Петро з 8-Б.\n\n"
        "👀 Перегляд розкладу — публічний. Його можуть бачити всі, навіть без верифікації."
    )

    HOW_WORKS: str = (
        "<b>Як це працює?</b>\n\n"
        "🧩 Ваш Telegram-акаунт зв'язується з вашим ім’ям у системі. "
        "Це означає, що тільки ви можете виконувати дії від вашого імені.\n\n"
        "❗️Доступ надається вручну — щоб уникнути фейкових акаунтів і приколістів."
    )


class TeacherVerifyHandler(BaseHandler):
    _user_back_callbacks: Dict[int, str] = {}

    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.send_msg_static,
            F.data == Triggers.HUB
        )

        self.router.callback_query.register(
            self.handle,
            TeacherVerifyCallback.filter()
        )

    async def send_msg(self, callback: CallbackQuery, back_callback: str) -> None:
        self._user_back_callbacks[callback.from_user.id] = back_callback
        await self.send_msg_static(callback)

    async def send_msg_static(self, callback: CallbackQuery) -> None:
        back_callback = self._user_back_callbacks.get(callback.from_user.id, "abc")

        await callback.message.edit_text(
            Messages.HUB,
            reply_markup=TeacherVerifyFAQ().get_keyboard(back_callback)
        )

    @classmethod
    async def handle(cls, callback: CallbackQuery, callback_data: TeacherVerifyCallback) -> None:
        method = getattr(TeacherVerifyEnum, callback_data.method)

        responses = {
            TeacherVerifyEnum.WHY_NEED: Messages.WHY_NEED,
            TeacherVerifyEnum.HOW_GET: Messages.HOW_GET,
            TeacherVerifyEnum.HOW_WORKS: Messages.HOW_WORKS
        }

        response = responses.get(method, "⚠️ Unknown method")

        await callback.message.edit_text(
            response,
            reply_markup=BackButton().get_keyboard(Triggers.HUB),
            parse_mode=ParseMode.HTML
        )
