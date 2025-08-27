import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import InterestingModel


class InterestingQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_date(self, date: datetime.date) -> str:
        """Повертає промпт за датою"""
        query = select(InterestingModel.prompt).where(InterestingModel.date == date)
        result = await self.session.execute(query)
        return result.scalar()

    async def add_new(self, prompt: str, date: datetime.date) -> None:
        try:
            obj = InterestingModel(prompt=prompt, date=date)
            self.session.add(obj)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
