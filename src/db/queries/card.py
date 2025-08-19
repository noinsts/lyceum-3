from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import CardModel
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
