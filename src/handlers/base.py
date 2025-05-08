from abc import ABC, abstractmethod

from aiogram import Router
from pytz import timezone

from src.utils import *
from src.db.database import Database
from src.sheets.connector import Sheet

class BaseHandler(ABC):
    def __init__(self):
        self.router = Router()
        self.log = setup_logger()
        self.db = Database()
        self.cfg = JSONLoader()
        self.kyiv_tz = timezone("Europe/Kyiv")
        self.wf = WeekFormat()

        self.sheet = Sheet()

        self.register_handler()

    @abstractmethod
    def register_handler(self) -> None:
        pass
