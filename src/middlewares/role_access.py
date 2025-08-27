from typing import Callable, Dict, Any, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.enums import UserType, DBUserType
from src.db.db import session_maker
from src.db.connector import DBConnector
from settings.developers import Developers
from settings.admins import Admins
from src.utils import setup_logger

logger = setup_logger()


class RoleAccessMiddleware(BaseMiddleware):
    def __init__(
            self,
            user_type: UserType,
            developers: Optional[Developers] = None,
            admins: Optional[Admins] = None
    ):
        self.user_type = user_type
        self.developers = developers or Developers()
        self.admins = admins or Admins()

    async def __call__(
            self,
            handler: Callable,
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ):
        user_id = event.from_user.id

        try:
            if not await self._has_access(user_id):
                return await self._send_access_denied(event)
        except Exception as e:
            logger.error(f"Error checking user access for {user_id}: {e}")
            return await self._send_access_denied(event)

        return await handler(event, data)

    async def _has_access(self, user_id: int) -> bool:
        """Перевіряє чи має користувач доступ до функціонала"""
        match self.user_type:
            case UserType.STUDENT:
                return await self._check_db_user_type(user_id, DBUserType.STUDENT)

            case UserType.TEACHER:
                return await self._check_db_user_type(user_id, DBUserType.TEACHER)

            case UserType.DEVELOPER:
                return user_id in self.developers.DEVELOPERS

            case UserType.ADMIN:
                return user_id in self.admins.ADMINS

            case _:
                return False

    @staticmethod
    async def _check_db_user_type(user_id: int, expected_type: DBUserType) -> bool:
        """Перевіряє тип користувача в БД"""
        try:
            async with session_maker() as session:
                db = DBConnector(session)
                db_user_type = await db.register.get_user_type(user_id)
                return db_user_type == expected_type
        except Exception as e:
            logger.warning(f"Failed to get user type for {user_id}: {e}")
            return False

    @staticmethod
    async def _send_access_denied(event: Message | CallbackQuery) -> None:
        """Надсилає повідомлення про відсутність доступу"""
        prompt = "⛔ У вас немає доступу до цієї команди."

        try:
            if isinstance(event, Message):
                await event.answer(prompt)
            elif isinstance(event, CallbackQuery):
                await event.answer(prompt, show_alert=True)
        except Exception as e:
            logger.error(f"Failed to send access denied message: {e}")

    @classmethod
    def for_students(cls, **kwargs) -> 'RoleAccessMiddleware':
        """Фабричний метод для створення middleware для студентів"""
        return cls(UserType.STUDENT, **kwargs)

    @classmethod
    def for_teachers(cls, **kwargs) -> 'RoleAccessMiddleware':
        """Фабричний метод для створення middleware для вчителів"""
        return cls(UserType.TEACHER, **kwargs)

    @classmethod
    def for_developers(cls, **kwargs) -> 'RoleAccessMiddleware':
        """Фабричний метод для створення middleware для розробників"""
        return cls(UserType.DEVELOPER, **kwargs)

    @classmethod
    def for_admins(cls, **kwargs) -> 'RoleAccessMiddleware':
        """Фабричний метод для створення middleware для адмінів"""
        return cls(UserType.ADMIN, **kwargs)
