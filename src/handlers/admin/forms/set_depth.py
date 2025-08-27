from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.db.connector import DBConnector
from src.exceptions import ValidationError
from src.decorators import next_state
from src.states.admin import DepthSubjectStates
from src.keyboards.inline import SelectForm, DepthSubjectKeyboard, SubmitKeyboard, BackToAdminHub
from src.filters.callbacks import FormsListCallback, DepthSubjectCallback
from src.enums import DepthSubjectEnum


class Triggers(str, Enum):
    HUB = "admin_form_controller_hub"
    HANDLER = "set_depth_subject"
    BACK_TO_FORMS = "set_select_form_depth_subject"
    SUBMIT = "submit_set_depth_subject_form"


@dataclass(frozen=True)
class Messages:
    NO_FORMS: str = (
        "❌ Помилка, класів не знайдено. Зверніться до розробників."
    )

    SELECT_FORM: str = (
        "📚 Оберіть клас, з яким будемо працювати:"
    )

    SELECT_SUBJECT: str = (
        "👨‍🎓 Оберіть предмет поглибленого вивчення"
    )

    CHANGE_DEPTH_SUBJECT: str = (
        "⚠️ Ви збираєтесь змінити поглиблений профіль для <b>{form}</b> класу.\n\n"
        "Зараз: <b>{old_depth_subject}</b>\n"
        "Новий: <b>{new_depth_subject}</b>\n\n"
        "✅ Підтвердіть дію або скасуйте."
    )

    NEW_DEPTH_SUBJECT: str = (
        "✅ Встановити <b>{depth_subject}</b> профіль для <b>{form}</b> класу?\n\n"
        "Підтвердіть дію або скасуйте."
    )

    SUBMIT: str = (
        "🎉 Поглиблений профіль встановлено\n\n"
        "📌 <b>{form}</b>\n"
        "📚 <b>{subject}</b>"
    )

    SUBMIT_ERROR: str = (
        "❌ Сталась помилка під час встановлення поглибленого профілю. "
        "Спробуйте знову, або зверніться до розробників."
    )


class SetDepthSubjectHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data.in_({Triggers.HANDLER, Triggers.BACK_TO_FORMS})
        )

        self.router.callback_query.register(
            self.get_form,
            FormsListCallback.filter(),
            DepthSubjectStates.waiting_for_form
        )

        self.router.callback_query.register(
            self.get_subject,
            DepthSubjectCallback.filter(),
            DepthSubjectStates.waiting_for_subject
        )

        self.router.callback_query.register(
            self.submit,
            F.data == Triggers.SUBMIT,
            DepthSubjectStates.waiting_for_confirmation
        )

    @classmethod
    @next_state(DepthSubjectStates.waiting_for_form)
    async def handler(cls, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        forms = await db.form.get_all_forms()

        if not forms:
            await callback.answer(Messages.NO_FORMS, show_alert=True)
            raise ValidationError

        await callback.message.edit_text(
            Messages.SELECT_FORM,
            reply_markup=SelectForm().get_keyboard(sorted(forms), False, Triggers.HUB)
        )

    async def get_form(self, callback: CallbackQuery, state: FSMContext, callback_data: FormsListCallback):
        await state.update_data(form=callback_data.form)
        await self.show_subjects(callback, state)

    @next_state(DepthSubjectStates.waiting_for_subject)
    async def show_subjects(self, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.SELECT_SUBJECT,
            reply_markup=DepthSubjectKeyboard().get_keyboard(Triggers.BACK_TO_FORMS)
        )

    async def get_subject(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: DepthSubjectCallback,
            db: DBConnector
    ) -> None:
        await state.update_data(subject=callback_data.subject)
        await self.show_confirmation(callback, state, db)

    @next_state(DepthSubjectStates.waiting_for_confirmation)
    async def show_confirmation(self, callback: CallbackQuery, state: FSMContext, db: DBConnector):
        data = await state.get_data()
        form = data.get("form")

        new_depth_subject = data.get("subject")
        new_depth_subject_enum = DepthSubjectEnum[new_depth_subject]
        new_depth_subject_display = new_depth_subject_enum.value

        old_depth_subject = await db.form.get_depth_subject(form)

        if old_depth_subject:
            old_depth_subject_display = old_depth_subject.value

            prompt = Messages.CHANGE_DEPTH_SUBJECT.format(
                form=form,
                new_depth_subject=new_depth_subject_display,
                old_depth_subject=old_depth_subject_display
            )
        else:
            prompt = Messages.NEW_DEPTH_SUBJECT.format(
                form=form,
                depth_subject=new_depth_subject_display
            )

        await callback.message.edit_text(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.HUB)
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()
        form = data.get("form")
        subject_str = data.get("subject")
        subject_enum = DepthSubjectEnum[subject_str]
        subject_display = subject_enum.value

        try:
            await db.form.set_depth_subject(form, subject_enum)

            await callback.message.edit_text(
                Messages.SUBMIT.format(
                    form=form,
                    subject=subject_display
                ),
                reply_markup=BackToAdminHub().get_keyboard(),
                parse_mode=ParseMode.HTML
            )

        except Exception as e:
            await callback.answer(Messages.SUBMIT_ERROR, show_alert=True)
            self.log.error(f"Помилка під час назначення профілю класу {e}", exc_info=True)

        finally:
            await state.clear()
