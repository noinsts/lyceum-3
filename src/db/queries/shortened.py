import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import ShortenedDayModel


class ShortenedQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_day(self, date: datetime.date) -> Optional[ShortenedDayModel]:
        """Повертає інформацію про день за датою"""
        query = select(ShortenedDayModel).where(ShortenedDayModel.date == date)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
