from aiogram.types import Message

from src.keyboards.inline import HubAdmin


class AdminHubHandler:
    @staticmethod
    async def show_hub(message: Message) -> None:
        await message.answer(
            "👑 Вітаємо в панелі адміністратора",
            # TODO: змінити текст
            reply_markup=HubAdmin().get_keyboard()
        )
