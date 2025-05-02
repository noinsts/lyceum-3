import os
import sys

# Додаємо поточну директорію до Python Path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Імпортуємо та запускаємо бота з src
from src.main import LyceumBot
import asyncio

if __name__ == "__main__":
    bot = LyceumBot()
    asyncio.run(bot.run())