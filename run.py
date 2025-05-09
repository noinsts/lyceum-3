import os
import sys

# Додаємо поточну директорію до Python Path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Імпортуємо та запускаємо бота з src
from src.main import LyceumBot, FlaskServer
import asyncio

if __name__ == "__main__":
    server = FlaskServer(port=8080)
    server.run_in_background()

    bot = LyceumBot()
    asyncio.run(bot.run())
