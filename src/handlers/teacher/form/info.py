from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.db.connector import DBConnector
from src.keyboards.inline import BackButton


class Triggers(str, Enum):
    HUB = "teacher_my_form_hub"
    HANDLER = "my_form_info"


@dataclass(frozen=True)
class Messages:
    NO_INFO: str = (
        "❌ Інформації по вашому класу не знайдено. "
        "Спробуйте знову, або зверніться до розробників"
    )

    INFO: str = (
        "📌 <b>Інформації про {form}</b>\n\n"
        "Поглиблений предмет: {depth_subject}\n"
        "Класний керівник: {form_teacher}"
    )


class InfoHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery, db: DBConnector) -> None:
        teacher_name = await db.register.get_teacher_name(callback.from_user.id)
        teacher_id = await db.verification.get_teacher_id(teacher_name)
        form = await db.form.get_form_by_teacher(teacher_id)

        info = await db.form.get_info(form)

        if not info:
            await callback.answer(Messages.NO_INFO, show_alert=True)
            return

        depth_subject = info.depth_subject.value if info.depth_subject else "не вказано"

        prompt = Messages.INFO.format(
            form=info.name,
            depth_subject=depth_subject,
            form_teacher=teacher_name
        )

        await callback.message.edit_text(
            prompt,
            reply_markup=BackButton().get_keyboard(Triggers.HUB),
            parse_mode=ParseMode.HTML
        )
