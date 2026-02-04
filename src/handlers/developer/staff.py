import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass

from aiogram import Bot, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from ..base import BaseHandler
from src.keyboards.inline import BackButton
from settings.admins import Admins
from settings.developers import Developers


@dataclass(frozen=True)
class Messages:
    TITLE: str = (
        "<b>Список {user_type} проєкту</b>:\n\n"
    )

    USER_INFO: str = (
        "👤 <b>{first_name}</b> (@{username}) | ID: <code>{uid}</code>\n"
    )

    USER_NOT_FOUND: str = (
        "❌ Користувача з ID <code>{uid}</code> не знайдено.\n"
    )


class SpecialListHandler(BaseHandler, ABC):
    @property
    @abstractmethod
    def triggers(self) -> Dict[str, str]:
        """
        Абстрактна властивість для визначення тригерів обробника.

        Використовується для реєстрації хендлера та формування кнопки 'Назад'.

        Returns:
            Dict[str, str]: Словник з ключами 'hub' (тригер для повернення)
                            та 'handler' (тригер для поточного хендлера).
        """
        pass

    @property
    @abstractmethod
    def user_type(self) -> str:
        """
        Абстрактна властивість для визначення типу користувачів.

        Приклад: "адміністраторів", "розробників". Це значення
        використовується для формування заголовка повідомлення.

        Returns:
            str: Рядок, що описує тип користувачів у множині.
        """
        pass

    @property
    @abstractmethod
    def user_ids(self) -> List[int]:
        """
        Абстрактна властивість, що повертає список ідентифікаторів користувачів.

        Returns:
            List[int]: Список Telegram User ID.
        """

    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == self.triggers['handler']
        )

    async def handler(self, callback: CallbackQuery) -> None:
        tasks = [self._get_user_id(callback.bot, uid) for uid in self.user_ids]
        user_info_list = await asyncio.gather(*tasks)

        prompt = self._create_prompt(user_info_list)

        await callback.message.edit_text(
            prompt,
            reply_markup=BackButton().get_keyboard(self.triggers['hub']),
            parse_mode=ParseMode.HTML
        )

    @classmethod
    async def _get_user_id(cls, bot: Bot, uid: int) -> Dict[str, Any]:
        """Асинхронно отримує інформацію про користувача"""
        try:
            info = await bot.get_chat(uid)

            return {
                "uid": uid,
                "username": info.username or 'не встановлено',
                "first_name": info.first_name or 'не встановлено',
                "found": True
            }

        except TelegramBadRequest:
            return {
                "uid": uid,
                "found": False
            }

    def _create_prompt(self, user_info_list: List[Dict[str, Any]]) -> str:
        """Створює повний текст повідомлення"""
        prompt = Messages.TITLE.format(user_type=self.user_type)
        for user_info in user_info_list:
            if user_info["found"]:
                prompt += Messages.USER_INFO.format(
                    uid=user_info['uid'],
                    username=user_info['username'],
                    first_name=user_info['first_name']
                )
            else:
                prompt += Messages.USER_NOT_FOUND.format(
                    uid=user_info['uid']
                )
        return prompt


class DevListHandler(SpecialListHandler):
    @property
    def triggers(self) -> Dict[str, str]:
        return {
            "hub": "dev_hub",
            "handler": "dev_dev_list"
        }

    @property
    def user_type(self) -> str:
        return "розробників"

    @property
    def user_ids(self) -> List[int]:
        return Developers.DEVELOPERS


class AdminListHandler(SpecialListHandler):
    @property
    def triggers(self) -> Dict[str, str]:
        return {
            "hub": "dev_hub",
            "handler": "dev_admin_list"
        }

    @property
    def user_type(self) -> str:
        return "адміністраторів"

    @property
    def user_ids(self) -> List[int]:
        return Admins.ADMINS
