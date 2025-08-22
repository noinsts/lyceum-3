import random
import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.db.connector import DBConnector
from src.keyboards.inline import BackButton
from src.enums import RarityCardsEnum
from src.db.models import CardModel


class Triggers(str, Enum):
    HUB = "card_hub"
    HANDLER = "new_card"


@dataclass(frozen=True)
class Messages:
    WAIT: str = (
        "Зачекай! ⏳ Наступний дроп буде доступний через {days} днів, {hours} годин і {minutes} хвилин."
    )

    ALL_COLLECTED: str = (
        "🎉 Схоже, що ви зібрали всі карти, вітаю! "
        "Тепер чекайте нових колекцій"
    )

    CARD_INFO: str = (
        "<b>Нова картка!</b>\n\n"
        "{color} <b>{name}</b>\n"
        "<b>Опис</b>: {desc}\n"
        "<b>Колекція</b>: {collection}\n"
        "<b>Рідкість</b>: {rarity}\n\n"
    )


class DropHandler(BaseHandler):
    RARITY_WEIGHTS = {
        RarityCardsEnum.DEFAULT: 50,
        RarityCardsEnum.RARE: 25,
        RarityCardsEnum.SUPERRARE: 15,
        RarityCardsEnum.EPIC: 7,
        RarityCardsEnum.LEGENDARY: 3,
    }

    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    async def handler(self, callback: CallbackQuery, db: DBConnector) -> None:
        last_time_drop = await db.card.get_last_drop_time(callback.from_user.id)

        if self._check_time_limit(last_time_drop):
            await callback.answer(self._format_time_left(last_time_drop), show_alert=True)
            return

        card = await self._get_card(callback.from_user.id, db)

        if not card:
            await callback.answer(Messages.ALL_COLLECTED, show_alert=True)
            return

        await callback.message.delete()
        await callback.message.answer_sticker(card.sticker_id)

        prompt = Messages.CARD_INFO.format(
            color=self._get_color(card.rarity),
            name=card.name,
            desc=card.description or "відсутній",
            collection=card.collection or "відсутня",
            rarity=card.rarity.value
        )

        await db.card.user_new_card(callback.from_user.id, card.id)

        await callback.message.answer(
            prompt,
            parse_mode=ParseMode.HTML,
            reply_markup=BackButton().get_keyboard(Triggers.HUB)
        )

    @staticmethod
    def _check_time_limit(last_drop_time: Optional[datetime.datetime]) -> bool:
        if not last_drop_time:
            return False

        last_drop_time_utc = last_drop_time.replace(tzinfo=datetime.timezone.utc)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        one_week_ago_utc = now_utc - datetime.timedelta(weeks=1)

        return last_drop_time_utc > one_week_ago_utc

    @staticmethod
    def _format_time_left(last_drop_time: datetime.datetime) -> str:
        time_left = datetime.timedelta(days=7) - (
                datetime.datetime.now(datetime.timezone.utc) -
                last_drop_time.replace(tzinfo=datetime.timezone.utc)
        )

        if time_left.total_seconds() <= 0:
            return Messages.WAIT.format(days=0, hours=0, minutes=0)

        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes = remainder // 60

        return Messages.WAIT.format(days=days, hours=hours, minutes=minutes)

    async def _get_card(self, user_id: int, db: DBConnector) -> Optional[CardModel]:
        available_cards = await db.card.get_available_cards_grouped_by_rarity(
            user_id, list(self.RARITY_WEIGHTS.keys())
        )

        if not available_cards:
            return None

        available_rarities = {
            rarity: weight for rarity, weight in self.RARITY_WEIGHTS.items()
            if rarity in available_cards and available_cards[rarity]
        }

        if not available_rarities:
            return None

        rarities, weights = zip(*available_rarities.items())
        selected_rarity = random.choices(rarities, weights=weights, k=1)[0]

        return random.choice(available_cards[selected_rarity])

    @staticmethod
    def _get_color(rarity: RarityCardsEnum) -> str:
        rarity_colors = {
            RarityCardsEnum.DEFAULT: "💚",
            RarityCardsEnum.RARE: "🩶",
            RarityCardsEnum.SUPERRARE: "💜",
            RarityCardsEnum.EPIC: "🩵",
            RarityCardsEnum.LEGENDARY: "💛"
        }
        return rarity_colors[rarity]
