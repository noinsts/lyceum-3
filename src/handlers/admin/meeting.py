from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..base import BaseHandler
from src.keyboards.inline import TeacherTypes
from src.utils.states import TeacherTypesStates


class Meeting(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.meeting,
            F.data == 'meeting'
        )

        self.router.callback_query.register(
            self.toggle_teacher,
            TeacherTypesStates.choosing_teacher,
            F.data.startswith("teacher_")
        )

        self.router.callback_query.register(
            self.finish_meeting,
            TeacherTypesStates.choosing_teacher,
            F.data == 'meeting_submit_button'
        )

    @staticmethod
    async def meeting(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(TeacherTypesStates.choosing_teacher)
        await state.update_data(selected_teacher_types=[])
        
        await callback.message.answer(
            "Оберіть тих, кого запрошуємо на вечірку ✨",
            reply_markup=TeacherTypes().get_keyboard()
        )

        # заглушка
        await callback.answer()

    @staticmethod
    async def toggle_teacher(callback: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        selected = data.get("selected_teacher_types", [])
        teacher_type = callback.data

        # логіка видалення вчителя зі списку, при повторному натисканні
        if teacher_type in selected:
            selected.remove(teacher_type)
            await callback.answer("Видалено!")
        else:
            selected.append(teacher_type)
            await callback.answer("Додано!")

        await state.update_data(selected_teacher_type=selected)

    @staticmethod
    async def finish_meeting(callback: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        selected = data.get("selected_teacher_types", [])

        if not selected:
            await callback.answer("Нічого поки не обрано", show_alert=True)
            return

        # TODO: зробить адекватні назви в text
        text = "🚀 <b>Ви запросили на нараду</b>:\n" + "\n".join(f"• {t}" for t in selected)

        await callback.message.answer(text, parse_mode=ParseMode.HTML)
        await state.clear()
        await callback.answer("Готово!")

        # TODO: прописать підтвердження
        # для цього є inline клавіатура SubmitKeyboard
