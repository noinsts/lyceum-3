"""
O magna Salnikova, munda peccata nostra, et veni ad nos, clamor noster auditur.
"""

"""
йобаний насос, я ніхуя в цьому коду не понімаю
хто це блять писав
"""

import asyncio
import os
import socket
from threading import Thread

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from flask import Flask
from pyngrok import ngrok

from src.handlers import get_all_router
from src.utils import setup_logger
from src.db.db import create_db

load_dotenv()
TOKEN = os.getenv("TOKEN")


class LyceumBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.log = setup_logger()

        self.dp.include_router(get_all_router())

    async def run(self):
        try:
            await create_db()
            self.log.info('Бот запущено!')
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.session.close()


class FlaskServer:
    def __init__(self, port: int = 8080):
        self.app = Flask(__name__)
        self.port = port
        self.log = setup_logger()
        self.setup_routes()

    def setup_routes(self) -> None:
        @self.app.route('/')
        def home():
            return "Бот живий", 200

    def run(self) -> None:
        self.app.run(host="0.0.0.0", port=self.port)

    def run_in_background(self) -> None:
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()

        public_url = ngrok.connect(self.port, "http")

        self.log.info(f"{public_url}")


if __name__ == "__main__":
    server = FlaskServer(port=8080)
    server.run_in_background()

    bot = LyceumBot()
    asyncio.run(bot.run())
