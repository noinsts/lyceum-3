import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import DayModel


class DayQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_day(self, date: datetime.date) -> Optional[DayModel]:
        """Повертає інформацію про день за датою"""
        query = select(DayModel).where(DayModel.date == date)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
