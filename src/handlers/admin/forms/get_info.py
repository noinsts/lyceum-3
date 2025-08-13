from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import BackToAdminHub, SelectForm
from src.filters.callbacks import FormsListCallback
from src.db.connector import DBConnector
from src.decorators import next_state
from src.states.admin import GetInfoStates


class Triggers(str, Enum):
    HUB = 'admin_form_controller_hub'
    HANDLER = "get_form_info"


@dataclass(frozen=True)
class Messages:
    NO_FORMS: str = (
        "❌ Помилка, класів не знайдено. Зверніться до розробників."
    )

    SELECT_FORM: str = (
        "📚 Оберіть клас, з яким будемо працювати:"
    )

    NO_INFO: str = (
        "❌ Інформації по цьому класу не знайдено. "
        "Спробуйте знову, або зверніться до розробників"
    )

    INFO: str = (
        "📌 <b>Інформації про {form}</b>\n\n"
        "Поглиблений предмет: {depth_subject}\n"
        "Класний керівник: {form_teacher}"
    )

class GetFormInfoHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.callback_query.register(
            self.get_form,
            FormsListCallback.filter(),
            GetInfoStates.waiting_for_forms
        )

    @classmethod
    @next_state(GetInfoStates.waiting_for_forms)
    async def handler(cls, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        forms = await db.form.get_all_forms()

        if not forms:
            await callback.answer(Messages.NO_FORMS, show_alert=True)
            return

        await callback.message.edit_text(
            Messages.SELECT_FORM,
            reply_markup=SelectForm().get_keyboard(sorted(forms), False, Triggers.HUB)
        )

    async def get_form(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: FormsListCallback,
            db: DBConnector
    ) -> None:
        await state.update_data(form=callback_data.form)
        await self._send_info(callback, state, db)

    @classmethod
    async def _send_info(cls, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        form = (await state.get_data()).get("form")

        form = await db.form.get_info(form)

        if not form:
            await callback.answer(Messages.NO_INFO, show_info=True)
            return

        teacher_name = await db.verification.get_teacher_name_by_id(form.teacher_id) or "не вказано"

        if form.depth_subject:
            depth_subject_display = form.depth_subject.value
        else:
            depth_subject_display = "не вказано"

        await callback.message.edit_text(
            Messages.INFO.format(
                form=form.name,
                depth_subject=depth_subject_display,
                form_teacher=teacher_name
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=BackToAdminHub().get_keyboard(Triggers.HUB)
        )
