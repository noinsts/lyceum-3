from aiogram.types import CallbackQuery

from src.keyboards.inline import TeacherVerifyFAQ


class TeacherVerify:
    @staticmethod
    async def send_msg(callback: CallbackQuery) -> None:
        await callback.message.answer(
            "🚫 Вибачте, ви не можете скористатись цією функцією, оскільки ви не верифікований вчитель",
            reply_markup=TeacherVerifyFAQ().get_keyboard()
        )
