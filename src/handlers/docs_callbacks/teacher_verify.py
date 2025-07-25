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

        self.router.callback_query.register(
            self.why_need_verify,
            F.data == 'why_need_verify'
        )

        self.router.callback_query.register(
            self.how_works_verify,
            F.data == 'how_works_verify'
        )

    @staticmethod
    async def how_get_verify(callback: CallbackQuery) -> None:
        await callback.answer()  # заглушка
        await callback.message.answer(
            "<b>Як отримати верифікацію?</b>\n\n"
            "Напишіть розробнику (Шостаку Андрію, чи як там мене звати) або тому, хто веде цей проєкт. "
            "Після швидкої перевірки вашого статусу (чи справді ви вчитель) — вам дадуть доступ.\n\n",
            parse_mode=ParseMode.HTML
        )
        # FIXME: змінити текст

    @staticmethod
    async def why_need_verify(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            "<b>Навіщо потрібна верифікація?</b>\n\n"
            "🔐 Верифікація потрібна для безпеки. Вона гарантує, що доступ до функцій типу:\n"
            "– створення/редагування олімпіад\n"
            "– дій від імені вчителя\n"
            "має лише справжній педагог, а не умовний Петро з 8-Б.\n\n"
            "👀 Перегляд розкладу — публічний. Його можуть бачити всі, навіть без верифікації.",
            parse_mode=ParseMode.HTML
        )

    @staticmethod
    async def how_works_verify(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            "<b>Як це працює?</b>\n\n"
            "🧩 Ваш Telegram-акаунт зв'язується з вашим ім’ям у системі. "
            "Це означає, що тільки ви можете виконувати дії від вашого імені.\n\n"
            "❗️Доступ надається вручну — щоб уникнути фейкових акаунтів і приколістів.",
            parse_mode=ParseMode.HTML
        )
