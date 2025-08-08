from loguru import logger
import sys


def setup_logger():
    # Видаляємо стандартний handler
    logger.remove()

    # Консоль з кольорами
    logger.add(sys.stderr,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

    # Файл з ротацією
    logger.add("logs/bot.log",
               rotation="50 MB",
               retention="2 weeks",
               compression="zip",
               format="{time} [{level}] {message}")

    # Окремо критичні помилки
    logger.add("logs/critical.log",
               filter=lambda record: record["level"].name in ["ERROR", "CRITICAL"])

    return logger
