from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import CardModel, UserCardModel
from ..schemas import CardSchema


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
