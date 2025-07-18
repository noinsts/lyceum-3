from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import OlympModel
from ..schemas import AddUserSchema


class OlympQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_member(self, data: AddUserSchema) -> None:
        """Додає нового учасника олімпіади."""
        try:
            member = OlympModel(**data.model_dump())
            self.session.add(member)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
