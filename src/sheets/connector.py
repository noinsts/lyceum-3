import os
import asyncio
from typing import Optional

import redis.asyncio as redis
from dotenv import load_dotenv

from src.sheets.models import *
from src.utils import setup_logger

load_dotenv()

SHEET_ID = os.getenv("SHEET_ID")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

logger = setup_logger()


class Sheet:
    _instance: Optional['Sheet'] = None
    _redis: Optional[redis.Redis] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        """Singleton pattern для уникнення множинних ініціалізацій"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    async def initialize(self):
        """Асинхронна ініціалізація"""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            # Ініціалізація Redis (для кешу + FSM)
            try:
                self._redis = redis.from_url(
                    REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20
                )
                # Тестуємо з'єднання
                await self._redis.ping()
            except Exception as e:
                logger.error(f"Warning: Redis не доступний ({e})")
                self._redis = None

            # Створюємо sheet об'єкти (спільна таблиця!)
            self.student = StudentSheet(
                spreadsheet_id=SHEET_ID,
                range_prefix="schedule!",
                redis=self._redis
            )

            self.teacher = TeacherSheet(
                spreadsheet_id=SHEET_ID,
                range_prefix="schedule!",
                redis=self._redis
            )

            # Ініціалізуємо базові класи (спільний Google API)
            await self.student.initialize()
            await self.teacher.initialize()

            # Встановлюємо зв'язок між моделями (спільний кеш)
            self.student._shared_cache_partner = self.teacher
            self.teacher._shared_cache_partner = self.student

            self._initialized = True

    async def close(self):
        """Закриваємо з'єднання"""
        if self._redis:
            await self._redis.aclose()  # aclose() в redis-py

    @property
    def redis(self) -> Optional[redis.Redis]:
        """Доступ до Redis (для FSM теж)"""
        return self._redis


# Глобальний екземпляр
_sheet_instance: Optional[Sheet] = None


async def get_sheet() -> Sheet:
    """Отримати ініціалізований Sheet екземпляр"""
    global _sheet_instance
    if _sheet_instance is None:
        _sheet_instance = Sheet()
        await _sheet_instance.initialize()
    return _sheet_instance


async def get_redis() -> Optional[redis.Redis]:
    """Отримати Redis для FSM aiogram"""
    sheet = await get_sheet()
    return sheet.redis


async def refresh_all_schedule() -> bool:
    """Оновити розклад для всіх моделей (спільна таблиця)"""
    sheet = await get_sheet()
    # Робимо refresh тільки для однієї моделі, бо таблиця спільна
    return await sheet.student.refresh_cache()
