import os
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import *
from utils import setup_logger

load_dotenv()
TOKEN = os.getenv("TOKEN")


class LyceumBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.log = setup_logger()

        self.register_handlers()


    def register_handlers(self):
        self.dp.include_router(CommonHandler().router)
        self.dp.include_router(RegisterHandler().router)
        self.dp.include_router(StudentHandler().router)
        self.dp.include_router(TeacherHandler().router)
        self.dp.include_router(StatsHandler().router)


    async def run(self):
        try:
            self.log.info('Бот запущено!')
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.session.close()


if __name__ == "__main__":
    bot = LyceumBot()
    asyncio.run(bot.run())
