from abc import ABC, abstractmethod

from aiogram import Router
from pytz import timezone

from src.utils import *
from src.sheets.connector import get_sheet


class BaseHandler(ABC):
    """
    Abstract base class for all bot handlers.

    This class defines the core structure and common utilities for handlers in the bot

    It provides:
        - A dedicated 'Router' for registering commands, messagess and callback handlers.
        - A logger instance for debugging and monitoring.
        - Lazy-loaded Google Sheet connection (via `get_sheet`).
        - Timezone and week-format utilities.
    """

    def __init__(self):
        """
        Initialize the base handler.

        Sets up:
            - Router
            - Logger
            - Ukrainian week name loader
            - Kyiv timezone
            - Week format helper
            - Registers the handler via `register_handler()` (must be implemented in subclasses)

        """
        self.router = Router()
        self.log = setup_logger()
        self._sheet = None

        # TODO: Consider romving if unused in production
        self.ukr_wn = JSONLoader("settings/ukranian_weekname.json")
        self.kyiv_tz = timezone("Europe/Kyiv")
        self.wf = WeekFormat()

        # Register handler routes defined in subclass
        self.register_handler()

    @abstractmethod
    def register_handler(self) -> None:
        """
        Abstract method for registering routes in the router.
        """
        pass

    def get_router(self) -> Router:
        """
        Get the router instance for this handler.
        """
        return self.router

    async def get_sheet(self):
        """
        Get a Google Sheet instance (lazy-loaded)
        """
        if self._sheet is None:
            self._sheet = await get_sheet()
        return self._sheet

    @property
    async def sheet(self):
        """
        Async property returning the Google Sheets instance

        Shortcut for:
            await self.get_sheet()

        Returns:
            Google Sheet object
        """
        return await self.get_sheet()
