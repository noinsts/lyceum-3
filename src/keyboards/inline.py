from typing import List, Optional, Tuple

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .base import BaseKeyboard
from src.enums import TeacherTypeEnum, DepthSubjectEnum
from src.filters.callbacks import (
    TeacherCategoryCallback, TeacherListCallback,
    FormsListCallback, DeveloperSearchEnum, DeveloperSearchCallback,
    DepthSubjectCallback
)


class BackButton(BaseKeyboard):
    def get_keyboard(self, back_callback: Optional[str] = None) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback)]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)


class BackToAdminHub(BaseKeyboard):
    def get_keyboard(self, back_callback: Optional[str] = "back_to_admin_hub") -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='🔙 Повернутись в хаб', callback_data=back_callback)]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)


class HubAdmin(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='📢 Створити оголошення', callback_data="announcement_hub")],
            [InlineKeyboardButton(text='📅 Змінити розклад', callback_data='admin_schedule_hub')],
            [InlineKeyboardButton(text='🫐 Керування класами', callback_data='admin_form_controller_hub')],
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class HubAdminSchedule(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='🧑🏻‍🎓', callback_data='change_schedule_student'),
             InlineKeyboardButton(text='🧑🏻‍🏫', callback_data='change_schedule_teacher')],
            [InlineKeyboardButton(text='🔃 Refresh', callback_data='refresh_cache_schedule')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_admin_hub')]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)


class FormControllerAdmin(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='Встановить Depth S.', callback_data='set_depth_subject')],
            [InlineKeyboardButton(text='Встановить класного керівника', callback_data='set_form_teacher')],
            [InlineKeyboardButton(text='Інформація про клас', callback_data='get_form_info')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_admin_hub')]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)


class DepthSubjectKeyboard(BaseKeyboard):
    def get_keyboard(self, back_callback: Optional[str] = None) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        for subject in DepthSubjectEnum:
            kb.button(
                text=subject.value,
                callback_data=DepthSubjectCallback(subject=subject.name).pack()
            )

        kb.button(text="⬅️ Назад", callback_data=back_callback)

        kb.adjust(1)
        return kb.as_markup()


class RedisControlPanel(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='📊 Cache Stats', callback_data="redis_cache_stats")],
            [InlineKeyboardButton(text='🗒 Get Schedule', callback_data="redis_get_schedule")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)


class AdminAnnouncementHub(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='🫱🏻‍🫲🏻 Запланувати нараду', callback_data='meeting')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_admin_hub')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class TeacherTypes(BaseKeyboard):
    def get_keyboard(
            self,
            is_multiply: Optional[bool] = True,
            back_callback: Optional[str] = "to_admin_schedule_hub"
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        for category in TeacherTypeEnum:
            kb.button(
                text=category.value,
                callback_data=TeacherCategoryCallback(name=category.name.lower()).pack()
            )

        if is_multiply:
            kb.button(text='✅ Готово', callback_data="selected_teacher_done")
            kb.button(text='ℹ️ Список доданих', callback_data="selected_teacher_list")

        kb.button(text='⬅️ Назад', callback_data=back_callback)

        kb.adjust(1)
        return kb.as_markup()


class TeacherList(BaseKeyboard):
    def get_keyboard(
            self,
            teacher_list: Optional[List[Tuple[int, str]]] = None,
            back_callback: Optional[str] = "admin_back_to_select_category"
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        if not teacher_list:
            teacher_list = []

        for teacher_id, teacher_name in teacher_list:
            kb.button(
                text=teacher_name,
                callback_data=TeacherListCallback(teacher_id=teacher_id).pack()
            )

        kb.button(text="🔙 Назад", callback_data=back_callback)

        kb.adjust(1)
        return kb.as_markup()


class AdminTeacherBackToCategory(BaseKeyboard):
    def get_keyboard(
            self,
            continue_adding: Optional[str] = "admin_back_to_select_category",
            message_callback: Optional[str] = "admin_teacher_schedule_done"
    ) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text="🔙 Продовжити додавання", callback_data=continue_adding)],
            [InlineKeyboardButton(text="✅ Відправити сповіщення", callback_data=message_callback)]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)


class SelectForm(BaseKeyboard):
    def get_keyboard(
            self,
            classes: Optional[List[str]] = None,
            is_multiply: Optional[bool] = True,
            back_callback: Optional[str] = "non"
    ) -> InlineKeyboardMarkup:
        main_kb = InlineKeyboardBuilder()
        control_kb = InlineKeyboardBuilder()

        for form in classes:
            main_kb.button(
                text=form,
                callback_data=FormsListCallback(form=form).pack()
            )

        main_kb.adjust(3)

        if is_multiply:
            control_kb.button(text='✅ Готово', callback_data="selected_forms_done")
            control_kb.button(text='ℹ️ Список доданих', callback_data="selected_forms_list")

        control_kb.button(text="🔙 Назад", callback_data=back_callback)

        control_kb.adjust(1)
        main_kb.attach(control_kb)
        return main_kb.as_markup()


class SubmitKeyboard(BaseKeyboard):
    def get_keyboard(self, submit_cb: str = "submit", cancel_cb: str = "cancel") -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='✅ Так, підтвердити', callback_data=submit_cb)],
            [InlineKeyboardButton(text='❌ Ні, почати заповнювати наново', callback_data=cancel_cb)]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class TeacherOlympHub(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='Створити нову олімпіаду', callback_data='create_new_olymp')],
            [InlineKeyboardButton(text='Редагувати наявну', callback_data='edit_olymp')],
            [InlineKeyboardButton(text='Видалити', callback_data='delete_olymp')],
            [InlineKeyboardButton(text='Список олімпіад', callback_data='list_olymps')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class DeveloperHub(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='Turn on khaos mode', callback_data="dev_khaos_on")],
            [InlineKeyboardButton(text='Access teacher account', callback_data="dev_access_hub")],
            [InlineKeyboardButton(text='Server stats', callback_data='dev_server_stats')],
            [InlineKeyboardButton(text='Broker', callback_data='dev_broker')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class DeveloperAccessHub(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='➕ Add', callback_data='dev_access_add')],
            [InlineKeyboardButton(text='📊 Stats', callback_data='dev_access_stats')],
            [InlineKeyboardButton(text='🚫 Block', callback_data='dev_access_block')],
            [InlineKeyboardButton(text='✅ Unblock', callback_data='dev_access_unblock')],
            [InlineKeyboardButton(text='ℹ️ Status', callback_data='dev_access_status')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)


class DeveloperSearchType(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(
                text="За ID",
                callback_data=DeveloperSearchCallback(method=DeveloperSearchEnum.BY_ID).pack()
            )],
            [InlineKeyboardButton(
                text="За ім'ям вчителя",
                callback_data=DeveloperSearchCallback(method=DeveloperSearchEnum.BY_TEACHER_NAME).pack()
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)


class TeacherVerifyFAQ(BaseKeyboard):
    def get_keyboard(self) -> InlineKeyboardMarkup:
        kb = [
            [InlineKeyboardButton(text='Як отримати верифікацію', callback_data='how_get_verify')],
            [InlineKeyboardButton(text='Нащо це потрібно', callback_data='why_need_verify')],
            [InlineKeyboardButton(text='Як це працює?', callback_data='how_works_verify')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=kb)
