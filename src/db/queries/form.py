from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import FormModel
from src.enums import DepthSubjectEnum


class FormQueries:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_forms(self) -> List[str]:
        query = select(FormModel.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_form_teacher(self, form: str) -> Optional[str]:
        query = select(FormModel.teacher_id).where(FormModel.name == form)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def has_form(self, teacher_id: int) -> bool:
        query = select(FormModel).where(
            FormModel.teacher_id == teacher_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_info(self, form: str) -> FormModel:
        query = select(FormModel).where(FormModel.name == form)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_depth_subject(self, form: str) -> Optional[DepthSubjectEnum]:
        query = select(FormModel.depth_subject).where(FormModel.name == form)
        result = await self.session.execute(query)
        return result.scalar()

    async def set_depth_subject(self, form: str, depth_subject: DepthSubjectEnum) -> None:
        try:
            query = (
                update(FormModel)
                .where(FormModel.name == form)
                .values(depth_subject=depth_subject)
            )
            await self.session.execute(query)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def set_teacher_form(self, form: str, teacher_id: int) -> None:
        try:
            query = (
                update(FormModel)
                .where(FormModel.name == form)
                .values(teacher_id=teacher_id)
            )
            await self.session.execute(query)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
