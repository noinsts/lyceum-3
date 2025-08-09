from enum import Enum

from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode
from pytz import timezone

from ..base import BaseHandler
from src.utils import JSONLoader
from src.sheets.connector import Sheet
from src.db.connector import DBConnector


class GenerateMessage:
    NO_FORM = (
        r"Сьогодні хмарно\.\.\. ☁️ Спробуйте завтра 0\_0 ||або просто станьте учнем||"
    )

    WEEKEND = {
        'message': "Вихідний! Have a rest",
        'sticker': "CAACAgEAAxkBAAEOZSxoE3COqmuPY034826sWOvB7WgTQgACjgEAAnY3dj9180psDptQBzYE"
    }

    NO_RESULTS = (
        "Уроків немає, везе"
    )

    async def send(self, message: Message, form: str, sheet: Sheet, offset: int = 0) -> None:

        """
        Обробка відправлення розкладу студентам за конкретним днем

        Args:
            message (Message): Повідомлення користувача.
            form (str): Клас користувача, наприклад "11-Б".
            sheet (Sheet): Google Sheet об'єкт, з якого береться розклад
            offset (int): Зміщення дня тижня, що використовується для отримання розкладу.
                0 — сьогодні,
                1 — завтра,
                2 — післязавтра і т.д.
        """

        if not form:
            await message.answer(self.NO_FORM, parse_mode=ParseMode.MARKDOWN_V2)
            return

        # tz = timezone("Europe/Kyiv")
        # day_num: int = (message.date.astimezone(tz).weekday() + offset) % 7

        day_num = 0

        if day_num > 4:
            await message.answer(self.WEEKEND['message'])
            await message.answer_sticker(self.WEEKEND['sticker'])
            return
        
        day_name = JSONLoader("settings/ukranian_weekname.json").get(str(day_num))

        results = await sheet.student.get_lessons(form, day_name)

        if not results:
            await message.answer(self.NO_RESULTS)
            return
        
        prompt = f"<b>Розклад уроків на {day_name.lower()}</b>:\n\n"

        for lesson_id, name, teacher in results:
            prompt += f"<b>{lesson_id}</b>: <b>{name}</b> з {teacher.replace(',', ' та')}\n\n"

        await message.answer(prompt, parse_mode=ParseMode.HTML)


class Triggers(str, Enum):
    TODAY_HANDLER = "📅 Розклад на сьогодні"
    TOMORROW_HANDLER = "🌇 Розклад на завтра"


class LessonsTodayHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.today, F.text == Triggers.TODAY_HANDLER)

    async def today(self, message: Message, db: DBConnector) -> None:
        user_class = await db.register.get_form(message.from_user.id)
        sheet = await self.get_sheet()
        await GenerateMessage().send(message, user_class, sheet, offset=0)


class LessonsTomorrowHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.tomorrow, F.text == Triggers.TOMORROW_HANDLER)

    async def tomorrow(self, message: Message, db: DBConnector) -> None:
        user_class = await db.register.get_form(message.from_user.id)
        sheet = await self.get_sheet()
        await GenerateMessage().send(message, user_class, sheet, offset=1)
