import os

import psutil
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from ..base import BaseHandler


class ServerStatsHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == "dev_server_stats"
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery) -> None:
        process = psutil.Process(os.getpid())
        cpu_usage = process.cpu_percent(interval=1)
        mem_info = process.memory_info()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        text = (
            f"📊 <b>Статистика системи та процесу</b>\n\n"
            f"🔹 CPU завантаження (всього): {psutil.cpu_percent()}%\n"
            f"🔹 CPU твого процесу: {cpu_usage}%\n"
            f"🔹 Вільна пам'ять: {ram.available / (1024**2):.2f} MB\n"
            f"🔹 Пам'ять процесу: {mem_info.rss / (1024**2):.2f} MB\n"
            f"🔹 Використання диску: {disk.percent}%"
        )

        await callback.message.answer(text, parse_mode=ParseMode.HTML)
