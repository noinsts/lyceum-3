import os
import json
import hashlib
import asyncio
from datetime import datetime, time
from typing import List, Optional, ClassVar

import redis.asyncio as redis
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from concurrent.futures import ThreadPoolExecutor

# Ідемо тільки 3 рівні вверх до кореня (lyceum-3)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Тепер просто йдемо до creds
CREDENTIALS_PATH = os.path.join(BASE_DIR, "creds", "credentials.json")


class BaseSheet:
    # Клас-атрибути для Singleton Google API сервісу
    _service: ClassVar[Optional[object]] = None
    _sheet: ClassVar[Optional[object]] = None
    _executor: ClassVar[Optional[ThreadPoolExecutor]] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __init__(self, spreadsheet_id: str, range_prefix: str, redis: Optional[redis.Redis] = None):
        self.spreadsheet_id = spreadsheet_id
        self.range_prefix = range_prefix
        self.LENGTH_SHEET = 7
        self.redis = redis

        # Префікс для кешування (відокремлено від FSM)
        self.cache_prefix = f"sheets_cache:{spreadsheet_id}"

        # Rate limiting для Google API
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms між запитами

    async def initialize(self):
        """Асинхронна ініціалізація Google API"""
        if BaseSheet._service is not None:
            return

        async with BaseSheet._lock:
            if BaseSheet._service is not None:
                return

            # ThreadPoolExecutor для Google API викликів
            BaseSheet._executor = ThreadPoolExecutor(max_workers=10)

            # Ініціалізуємо Google API в окремому потоці
            loop = asyncio.get_event_loop()
            service_data = await loop.run_in_executor(
                BaseSheet._executor,
                self._init_google_service
            )

            BaseSheet._service = service_data['service']
            BaseSheet._sheet = service_data['sheet']
            print("Google Sheets API ініціалізовано")

    def _init_google_service(self):
        """Синхронна ініціалізація Google сервісу"""
        creds = Credentials.from_service_account_file(
            filename=CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)
        return {
            'service': service,
            'sheet': service.spreadsheets()
        }

    def _get_cache_key(self, method_name: str, range_name: str) -> str:
        """Генерує ключ для кешу"""
        key_data = f"{method_name}:{range_name}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]  # Коротший хеш
        return f"{self.cache_prefix}:{key_hash}"

    async def _get_from_cache(self, cache_key: str) -> Optional[List[List[str]]]:
        """Отримує дані з кешу"""
        if not self.redis:
            return None

        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except (redis.RedisError, json.JSONDecodeError) as e:
            print(f"Cache read error: {e}")
        return None

    async def _save_to_cache(self, cache_key: str, data: List[List[str]]) -> None:
        """Зберігає дані в кеші БЕЗ TTL (тільки manual refresh)"""
        if not self.redis:
            return

        try:
            await self.redis.set(
                cache_key,
                json.dumps(data, ensure_ascii=False)
                # Без TTL! Кеш живе до manual refresh
            )
        except redis.RedisError as e:
            print(f"Cache write error: {e}")

    async def _make_sheets_request(self, range_name: str) -> List[List[str]]:
        """Асинхронний запит до Google Sheets API з rate limiting"""
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)

        self._last_request_time = asyncio.get_event_loop().time()

        # Виконуємо запит в окремому потоці
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            BaseSheet._executor,
            self._sync_sheets_request,
            range_name
        )

        return result.get("values", [])

    def _sync_sheets_request(self, range_name: str):
        """Синхронний запит до Google Sheets"""
        return BaseSheet._sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()

    async def get_all(self) -> List[List[str]]:
        """Отримує всі дані (з кешем)"""
        await self.initialize()

        range_name = f"{self.range_prefix}A2:G"
        cache_key = self._get_cache_key("get_all", range_name)

        # Спочатку кеш
        cached_data = await self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Якщо немає - запитуємо API
        data = await self._make_sheets_request(range_name)

        # Зберігаємо в кеші
        await self._save_to_cache(cache_key, data)

        return data

    async def get_all_new(self) -> List[List[str]]:
        """Отримує дані з templateDemo (з кешем)"""
        await self.initialize()

        range_name = "templateDemo"
        cache_key = self._get_cache_key("get_all_new", range_name)

        # Спочатку кеш
        cached_data = await self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Якщо немає - запитуємо API
        data = await self._make_sheets_request(range_name)

        # Зберігаємо в кеші
        await self._save_to_cache(cache_key, data)

        return data

    def parse_start_time(self, period: str) -> time:
        """Парсинг часу (синхронний, швидкий)"""
        start_str = period.split('-')[0]
        return datetime.strptime(start_str, "%H%M").time()

    async def refresh_cache(self) -> bool:
        """MANUAL REFRESH - очищає кеш і перезавантажує дані"""
        if not self.redis:
            return False

        try:
            # Очищуємо весь кеш цього spreadsheet
            pattern = f"{self.cache_prefix}:*"
            keys_to_delete = []

            # redis-py async scan
            async for key in self.redis.scan_iter(match=pattern, count=100):
                keys_to_delete.append(key)

            if keys_to_delete:
                await self.redis.delete(*keys_to_delete)

            print(f"Cache cleared for {self.spreadsheet_id}")

            # Опціонально: одразу перезавантажити дані
            await self.get_all()
            await self.get_all_new()

            return True
        except redis.RedisError as e:
            print(f"Refresh cache error: {e}")
            return False

    async def get_cache_stats(self) -> dict:
        """Статистика кешу (для адмін панелі)"""
        if not self.redis:
            return {"status": "Redis не підключено"}

        try:
            pattern = f"{self.cache_prefix}:*"
            keys = []
            async for key in self.redis.scan_iter(match=pattern, count=100):
                keys.append(key)

            info = await self.redis.info('memory')

            return {
                "status": "OK",
                "cached_ranges": len(keys),
                "redis_memory": info.get('used_memory_human', 'N/A'),
                "keys": keys
            }
        except redis.RedisError as e:
            return {"status": f"Error: {e}"}

    @classmethod
    async def cleanup(cls):
        """Закрити executor при завершенні роботи"""
        if cls._executor:
            cls._executor.shutdown(wait=True)
            cls._executor = None
