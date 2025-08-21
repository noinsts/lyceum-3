from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.keyboards.inline import PaginationKeyboard
from src.db.connector import DBConnector
from src.enums import RarityCardsEnum
from src.filters.callbacks import PaginationCallback
from src.states import CardListStates
from src.decorators import next_state
from src.exceptions import ValidationError
from src.db.models import CardModel


class Triggers(str, Enum):
    HUB = "card_hub"
    HANDLER = "my_card_collection"
    CURR_PAGE = "current_page"


@dataclass(frozen=True)
class Messages:
    NO_CARDS: str = (
        "У вас ще немає карток, але не пізно це виправити"
    )

    TITLE: str = (
        "<b>Колекційна картка користувача {first_name}</b>\n\n"
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

        self.router.callback_query.register(
            self.handle_pagination,
            PaginationCallback.filter(),
            CardListStates.waiting_for_actions
        )

        self.router.callback_query.register(
            self.current_page,
            F.data == Triggers.CURR_PAGE,
            CardListStates.waiting_for_actions
        )

    @next_state(CardListStates.waiting_for_actions)
    async def handler(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        inventory = await db.card.get_user_cards(callback.from_user.id)

        if not inventory:
            await callback.answer(Messages.NO_CARDS, show_alert=True)
            raise ValidationError

        await state.update_data(inventory=inventory)

        response = self._get_card_info(0, callback.from_user.first_name, inventory)

        await callback.message.edit_text(
            response,
            parse_mode=ParseMode.HTML,
            reply_markup=PaginationKeyboard().get_keyboard(0, len(inventory), Triggers.HUB)
        )

    async def handle_pagination(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            callback_data: PaginationCallback
    ) -> None:
        page = callback_data.page

        inventory = (await state.get_data()).get("inventory")
        info = self._get_card_info(page, callback.from_user.first_name, inventory)

        await callback.message.edit_text(
            info,
            parse_mode=ParseMode.HTML,
            reply_markup=PaginationKeyboard().get_keyboard(page, len(inventory), Triggers.HUB)
        )

    @classmethod
    async def current_page(cls, callback: CallbackQuery) -> None:
        await callback.answer()

    # ==============================
    # Приватні методи
    # ==============================

    def _get_card_info(self, page: int, first_name: str, inventory: List[CardModel]) -> Optional[str]:
        if not (0 <= page < len(inventory)):
            return None

        card = inventory[page]

        return "\n".join([
            Messages.TITLE.format(first_name=first_name or "Користувач"),
            Messages.CARD_INFO.format(
                color=self._get_color(card.rarity),
                name=card.name,
                desc=card.description or "Без опису",
                collection=card.collection or "Відсутня",
                rarity=card.rarity.value
            )
        ])

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
