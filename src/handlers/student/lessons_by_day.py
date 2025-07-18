from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.utils import JSONLoader
from src.sheets.connector import Sheet
from src.db.connector import DBConnector


class GenerateMessage:
    @staticmethod
    async def send(message: Message, form: str, offset: int = 0, tz = None, wf = None) -> None:

        """
        Обробка відправки розкладу студентам за конкретний днем

        Args:
            message (Message): Повідомлення користувача.
            form (str): Клас користувача, наприклад "11-Б".
            offset (int): Зміщення дня тижня, що використовується для отримання розкладу.
                0 — сьогодні,
                1 — завтра,
                2 — післязавтра і т.д.
            tz (tzinfo): Часовий пояс для коректного визначення дня тижня.
            wf: Об'єкт або функція для обробки назв уроків та вчителів.

        """

        if not form:
            await message.answer(
                r"Сьогодні хмарно\.\.\. ☁️ Спробуйте завтра 0\_0 ||або просто станьте учнем||",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        
        day_num: int = (message.date.astimezone(tz).weekday() + offset) % 7

        if day_num > 4:
            await message.answer("Вихідний! Have a rest")
            await message.answer_sticker("CAACAgEAAxkBAAEOZSxoE3COqmuPY034826sWOvB7WgTQgACjgEAAnY3dj9180psDptQBzYE")
            return
        
        day_name = JSONLoader("settings/ukranian_weekname.json").get(str(day_num))
        results = Sheet().student.get_lessons(form, day_name)

        if not results:
            await message.answer("У вас сьогодні вихідний")
            return
        
        prompt = f"<b>Розклад уроків на {day_name.lower()}</b>:\n\n"

        for lesson_id, name, teacher in results:
            # парсинг назви уроку та вчителя за чисельником / знаменником тижня
            name, teacher = wf.student(name, teacher)
            if name:
                prompt += f"<b>{lesson_id}</b>: <b>{name}</b> з {teacher.replace(',', ' та')}\n\n"

        await message.answer(
            prompt,
            parse_mode=ParseMode.HTML
        )
        

class LessonsTodayHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.today, F.text == '📅 Розклад на сьогодні')

    async def today(self, message: Message, db: DBConnector) -> None:
        user_class = await db.register.get_form(message.from_user.id)
        await GenerateMessage.send(message, user_class, offset=0, tz=self.kyiv_tz, wf=self.wf)


class LessonsTomorrowHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.tomorrow, F.text == '🌇 Розклад на завтра')

    async def tomorrow(self, message: Message, db: DBConnector) -> None:
        user_class = await db.register.get_form(message.from_user.id)
        await GenerateMessage.send(message, user_class, offset=1, tz=self.kyiv_tz, wf=self.wf)
