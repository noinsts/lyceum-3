import os
from enum import Enum

import psutil
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from ..base import BaseHandler
from src.keyboards.inline import BackButton


class Triggers(str, Enum):
    HUB = "dev_hub"
    HANDLER = "dev_server_stats"


class ServerStatsHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
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
            f"🔹 <b>CPU завантаження (всього)</b>: {psutil.cpu_percent()}%\n"
            f"🔹 <b>CPU твого процесу</b>: {cpu_usage}%\n"
            f"🔹 <b>Вільна пам'ять</b>: {ram.available / (1024**2):.2f} MB\n"
            f"🔹 <b>Пам'ять процесу</b>: {mem_info.rss / (1024**2):.2f} MB\n"
            f"🔹 <b>Використання диску</b>: {disk.percent}%"
        )

        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=BackButton().get_keyboard(Triggers.HUB)
        )
