import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import DayModel
from ..schemas import DaySchema


class DayQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_day(self, date: datetime.date) -> Optional[DayModel]:
        """Повертає інформацію про день за датою"""
        query = select(DayModel).where(DayModel.date == date)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def set_day(self, day: DaySchema) -> None:
        """Встановлює статус для конкретного дня"""
        try:
            obj = DayModel(**day.model_dump())
            self.session.add(obj)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
