from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.handlers.base import BaseHandler


class CancelFSMHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(
            self.handler,
            Command("cancel"),
            flags={"priority": 1_000_000}
        )

    @staticmethod
    async def handler(message: Message, state: FSMContext) -> None:
        """Хендер очищує FSM стан та надсилає відповідний feedback"""
        if not await state.get_state():
            await message.answer("📌 Ви не маєте активних станів.")
            return

        await message.answer("❌ Скасовано.")
        await state.clear()
