from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import BackButton
from src.db.connector import DBConnector
from src.enums import RarityCardsEnum


class Triggers(str, Enum):
    HUB = "card_hub"
    HANDLER = "my_card_collection"


@dataclass(frozen=True)
class Messages:
    NO_CARDS: str = (
        "У вас ще немає карток, але не пізно це виправити"
    )

    TITLE: str = (
        "<b>Список карток користувача {first_name}</b>\n\n"
    )

    CARD_INFO: str = (
        "{color} <b>{name}</b>\n"
        "<b>Опис</b>: {desc}\n"
        "<b>Колекція</b>: {collection}\n"
        "<b>Рідкість</b>: {rarity}\n\n"
    )


class InventoryHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

    @classmethod
    async def handler(cls, callback: CallbackQuery, db: DBConnector) -> None:
        inventory = await db.card.get_user_cards(callback.from_user.id)

        if not inventory:
            await callback.answer(Messages.NO_CARDS, show_alert=True)
            return

        rarity_colors = {
            RarityCardsEnum.DEFAULT: "💚",
            RarityCardsEnum.RARE: "🩶",
            RarityCardsEnum.SUPERRARE: "💜",
            RarityCardsEnum.EPIC: "🩵",
            RarityCardsEnum.LEGENDARY: "💛"
        }

        response = [Messages.TITLE.format(first_name=callback.from_user.first_name)]

        for card in inventory:
            color = rarity_colors.get(card.rarity, "")

            response.append(Messages.CARD_INFO.format(
                color=color,
                name=card.name,
                desc=card.description or "Без опису",
                collection=card.collection or "Відсутня",
                rarity=card.rarity.value
            ))

        await callback.message.edit_text(
            "\n".join(response),
            parse_mode=ParseMode.HTML,
            reply_markup=BackButton().get_keyboard(Triggers.HUB)
        )
