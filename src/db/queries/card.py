import datetime
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import CardModel, UserCardModel
from ..schemas import CardSchema
from src.enums import RarityCardsEnum


class CardQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def new_card(self, data: CardSchema) -> None:
        try:
            card = CardModel(**data.model_dump())
            self.session.add(card)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_user_cards(self, user_id: int) -> Optional[List[CardModel]]:
        """Повертає всі CardModel конкретного user_id"""
        query = (
            select(CardModel)
            .join(UserCardModel, UserCardModel.card_id == CardModel.id)
            .where(UserCardModel.user_id == user_id)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_card_by_id(self, card_id: int) -> Optional[CardModel]:
        """Повертає CardModel за ID картки"""
        query = select(CardModel).where(CardModel.id == card_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_last_drop_time(self, user_id: int) -> Optional[datetime.datetime]:
        """Повертає час останньої випавшої користувачу картки"""
        query = (
            select(func.max(UserCardModel.created))
            .where(UserCardModel.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def user_new_card(self, user_id: int, card_id: int) -> None:
        try:
            obj = UserCardModel(user_id=user_id, card_id=card_id)
            self.session.add(obj)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_available_cards_grouped_by_rarity(
            self,
            user_id: int,
            rarities: List[RarityCardsEnum]
    ) -> dict[RarityCardsEnum, List[CardModel]]:
        """
        Повертає доступні картки (які користувач ще не має), згруповані за рідкістю.
        Один запит замість циклу - значно швидше!
        """
        user_cards_subquery = (
            select(UserCardModel.card_id)
            .where(UserCardModel.user_id == user_id)
            .subquery()
        )

        query = (
            select(CardModel)
            .where(
                CardModel.rarity.in_(rarities),
                ~CardModel.id.in_(select(user_cards_subquery.c.card_id))
            )
            .order_by(CardModel.rarity, CardModel.id)
        )

        result = await self.session.execute(query)
        cards = result.scalars().all()

        grouped_cards = {}
        for card in cards:
            if card.rarity not in grouped_cards:
                grouped_cards[card.rarity] = []
            grouped_cards[card.rarity].append(card)

        return grouped_cards
