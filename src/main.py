import os
import asyncio
import socket
from threading import Thread

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask
from pyngrok import ngrok

from src.handlers import *
from src.utils import setup_logger

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
        self.dp.include_router(AllHandler().router)


    async def run(self):
        try:
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
