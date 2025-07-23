from aiogram.types import Message

from src.keyboards.inline import DeveloperHub


class DevHubHandler:
    @staticmethod
    async def show_hub(message: Message) -> None:
        await message.answer(
            "The developer mode has been activated. 🚀",
            reply_markup=DeveloperHub().get_keyboard()
        )
