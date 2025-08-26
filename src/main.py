import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv

from src.bot_instance import set_bot
from src.handlers import get_all_router
from src.utils import setup_logger
from src.db.db import create_db
from src.middlewares import DBMiddleware, LoggingMiddleware, AntiSpamMiddleware
from src.sheets.connector import get_sheet, get_redis

load_dotenv()
TOKEN = os.getenv("TOKEN")


class LyceumBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        set_bot(self.bot)

        self.storage = None
        self.dp = None
        self.log = setup_logger()

    async def run(self):
        try:
            redis = await get_redis()

            if redis is None:
                self.log.warning("Redis недоступний! Використовую MemoryStorage для FSM")
                self.storage = MemoryStorage()
            else:
                self.log.info("Redis підключено успішно!")
                self.storage = RedisStorage(redis=redis)

            self.dp = Dispatcher(storage=self.storage)

            sheet = await get_sheet()
            self.log.info(f"Google Sheets підключено! {str(sheet)}")

            # підключення anti spam middleware
            anti_spam_middleware = AntiSpamMiddleware()
            self.dp.message.middleware(anti_spam_middleware)
            self.dp.callback_query.middleware(anti_spam_middleware)

            # підключення database middleware
            db_middleware = DBMiddleware()
            self.dp.message.middleware(db_middleware)
            self.dp.callback_query.middleware(db_middleware)

            # підключення logging middleware
            logging_middleware = LoggingMiddleware()
            self.dp.message.middleware(logging_middleware)
            self.dp.callback_query.middleware(logging_middleware)

            self.dp.include_router(get_all_router())

            await create_db()
            self.log.info("БД підключено")

            self.log.info('Бот запущено!')
            await self.dp.start_polling(self.bot)

        except Exception as e:
            self.log.error(f"Помилка запуску бота: {e}")
            raise

        finally:
            sheet = await get_sheet()
            await sheet.close()

            await self.bot.session.close()


if __name__ == "__main__":
    bot = LyceumBot()
    asyncio.run(bot.run())
