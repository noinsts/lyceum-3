from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...base import BaseHandler
from src.keyboards.inline import TeacherTypes, TeacherList, SelectForm, SubmitKeyboard, BackButton
from src.states.admin import TeacherFormStates
from src.filters.callbacks import TeacherCategoryCallback, TeacherListCallback, FormsListCallback
from src.db.connector import DBConnector
from src.enums import TeacherTypeEnum
from src.decorators import next_state
from src.exceptions import ValidationError


class Triggers(str, Enum):
    HUB = "admin_form_controller_hub"
    HANDLER = "set_form_teacher"
    BACK_TO_FORM = "back_to_forms_selection"
    BACK_TO_CATEGORY = "set_tform_get_category"
    SUBMIT = "submit_set_form_teacher"
    CANCEL = "admin_form_controller_hub"


@dataclass(frozen=True)
class Messages:
    NO_FORMS: str = (
        "❌ Помилка, класів не знайдено. Зверніться до розробників."
    )

    SELECT_FORM: str = (
        "📚 Оберіть клас, з яким будемо працювати:"
    )

    SELECT_CATEGORY: str = (
        "👤 Оберіть категорію вчителя, якого хочете призначити класним керівником:"
    )

    NO_CATEGORY_TEACHER: str = (
        "❌ Не вдалося знайти вчителів у цій категорії. "
        "Можливо, база ще не заповнена."
    )

    SELECT_TEACHER: str = (
        "🔍 Оберіть конкретного викладача зі списку:"
    )

    TEACHER_HAS_FORM: str = (
        "❌ {teacher_name} вже є класним керівником іншого класу.\n"
        "Спочатку зніміть його з тієї посади."
    )

    CHANGE_TEACHER_FORM: str = (
        "⚠️ Ви збираєтесь змінити класного керівника для <b>{form}</b> класу.\n\n"
        "Зараз: <b>{form_teacher}</b>\n"
        "Новий: <b>{teacher_name}</b>\n\n"
        "✅ Підтвердіть дію або скасуйте."
    )

    NEW_TEACHER_FORM: str = (
        "✅ Призначити <b>{teacher_name}</b> класним керівником <b>{form}</b> класу?\n\n"
        "Підтвердіть дію або скасуйте."
    )

    SUBMIT: str = (
        "🎉 Класного керівника успішно встановлено!\n\n"
        "📌 Клас: <b>{form}</b>\n"
        "👤 Викладач: <b>{teacher_name}</b>"
    )

    SUBMIT_ERROR: str = (
        "❌ Сталася помилка під час призначення класного керівника. "
        "Спробуйте ще раз або зверніться до розробників."
    )


class SetFormTeacherHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.callback_query.register(
            self.show_forms,
            F.data == Triggers.BACK_TO_FORM,
            TeacherFormStates.waiting_for_category
        )

        self.router.callback_query.register(
            self.get_form,
            FormsListCallback.filter(),
            TeacherFormStates.waiting_for_form,
        )

        self.router.callback_query.register(
            self.show_category,
            TeacherFormStates.waiting_for_name,
            F.data == Triggers.BACK_TO_CATEGORY
        )

        self.router.callback_query.register(
            self.get_category,
            TeacherCategoryCallback.filter(),
            TeacherFormStates.waiting_for_category
        )

        self.router.callback_query.register(
            self.get_name,
            TeacherListCallback.filter(),
            TeacherFormStates.waiting_for_name
        )

        self.router.callback_query.register(
            self.submit,
            TeacherFormStates.waiting_for_confirmation,
            F.data == Triggers.SUBMIT
        )

    async def handler(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        await callback.answer()
        await self.show_forms(callback, state, db)

    @staticmethod
    async def show_forms(callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        forms = await db.form.get_all_forms()

        if not forms:
            await callback.answer(Messages.NO_FORMS, show_alert=True)
            return

        await state.set_state(TeacherFormStates.waiting_for_form)
        await callback.message.edit_text(
            Messages.SELECT_FORM,
            reply_markup=SelectForm().get_keyboard(sorted(forms), False, "admin_form_controller_hub")
        )

    async def get_form(
            self,
            callback: CallbackQuery,
            callback_data: FormsListCallback,
            state: FSMContext
    ) -> None:
        await state.update_data(form=callback_data.form)
        await self.show_category(callback, state)

    @classmethod
    @next_state(TeacherFormStates.waiting_for_category)
    async def show_category(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.SELECT_CATEGORY,
            reply_markup=TeacherTypes().get_keyboard(False, Triggers.BACK_TO_FORM)
        )

    @classmethod
    @next_state(TeacherFormStates.waiting_for_name)
    async def get_category(
            cls,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: TeacherCategoryCallback,
            db: DBConnector
    ) -> None:
        category = TeacherTypeEnum[callback_data.name.upper()]
        teachers = await db.qualification.get_by_category(category)

        if not teachers:
            await callback.answer(Messages.NO_CATEGORY_TEACHER, show_alert=True)
            raise ValidationError

        await callback.message.edit_text(
            Messages.SELECT_TEACHER,
            reply_markup=TeacherList().get_keyboard(teachers, Triggers.BACK_TO_CATEGORY)
        )

    @classmethod
    @next_state(TeacherFormStates.waiting_for_confirmation)
    async def get_name(
            cls,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: TeacherListCallback,
            db: DBConnector
    ) -> None:
        teacher_id = callback_data.teacher_id

        teacher_name = await db.verification.get_teacher_name_by_id(teacher_id)

        if await db.form.has_form(teacher_id):
            await callback.answer(
                Messages.TEACHER_HAS_FORM.format(teacher_name=teacher_name),
                show_alert=True
            )
            raise ValidationError

        await state.update_data(teacher_id=teacher_id, teacher_name=teacher_name)

        form = (await state.get_data()).get("form")

        before_teacher_id = await db.form.get_form_teacher(form)

        if before_teacher_id:
            before_teacher_name = await db.verification.get_teacher_name_by_id(before_teacher_id)
            prompt = Messages.CHANGE_TEACHER_FORM.format(
                teacher_name=teacher_name,
                form=form,
                form_teacher=before_teacher_name
            )
        else:
            prompt = Messages.NEW_TEACHER_FORM.format(
                teacher_name=teacher_name,
                form=form
            )

        await callback.message.edit_text(
            prompt,
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.CANCEL),
            parse_mode=ParseMode.HTML
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        await callback.answer()

        data = await state.get_data()
        form = data.get("form")
        teacher_id = data.get("teacher_id")
        teacher_name = data.get("teacher_name")

        try:
            await db.form.set_teacher_form(form, teacher_id)

            await callback.message.edit_text(
                Messages.SUBMIT.format(form=form, teacher_name=teacher_name),
                reply_markup=BackButton().get_keyboard(Triggers.HUB),
                parse_mode=ParseMode.HTML
            )

        except Exception as e:
            await callback.answer(Messages.SUBMIT_ERROR, show_alert=True)
            self.log.error(f"Помилка під час назначення вчителя на посаду класного керівника: {e}", exc_info=True)

        finally:
            await state.clear()
