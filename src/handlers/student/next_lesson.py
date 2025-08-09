from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler

from src.db.connector import DBConnector


class NextLessonHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.WEEKEND_STICKER = "CAACAgEAAxkBAAEOZSxoE3COqmuPY034826sWOvB7WgTQgACjgEAAnY3dj9180psDptQBzYE"
        self.WEEKEND_PROMPT = "Вихідний! Have a rest"

    def register_handler(self) -> None:
        self.router.message.register(self.handler, F.text == '➡️ Наступний урок')

    @classmethod
    async def handler(cls, message: Message) -> None:
        await message.answer("🔐 Цей розділ зачинений до кращих часів.")

    async def legacy(self, message: Message, db: DBConnector) -> None:
        """Обробка кнопки ➡️ Наступний урок"""
        user_class = await db.register.get_form(message.from_user.id)

        if not user_class:
            await message.answer("Вибачте, інформації про вас не знайдено, скористайтесь командою /register")
            return

        day: int = message.date.astimezone(self.kyiv_tz).weekday()

        if day > 4:
            await message.answer(self.WEEKEND_PROMPT)
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        day: str = self.ukr_wn.get(str(day))

        time = message.date.astimezone(self.kyiv_tz).time()

        # time = "08:29:00"
        #
        # await message.answer(
        #     f"DEBUG:\n\n"
        #     f"{time=}\n"
        #     f"{day=}"
        # )

        # time = datetime.strptime(time, "%H:%M:%S").time()

        results = self.sheet.student.next_lesson(day, user_class, time)

        if not results:
            await message.answer("На сьогодні все...")
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        l_num, to, subj, teach = results

        subj, teach = self.wf.student(subj, teach)

        if not subj:
            await message.answer("На сьогодні все...")
            await message.answer_sticker(self.WEEKEND_STICKER)
            return

        await message.answer(
            f"<b>Наступний урок:</b>\n\n"
            f"#️⃣ {l_num}\n"
            f"📄 {subj}\n"
            f"👨🏻‍🏫 {teach.replace(",", " та")}\n"
            f"🕗 Урок почнеться через <b>{to.seconds // 60 + to.days * 24 * 60} хв.</b>",
            parse_mode=ParseMode.HTML
        )
