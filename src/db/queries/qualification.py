from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from ..models import TeacherModel, TeacherQualificationModel
from src.enums import TeacherTypeEnum

# data: List[Tuple[int, TeacherTypeEnum]] = [
#     (3, TeacherTypeEnum.PHILOLOGY),
#     (11, TeacherTypeEnum.STEM)
# ]


class QualificationQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_category(self, category: TeacherTypeEnum) -> List[Tuple[int, str]]:
        """
        Повертає список вчителів вказаною категорією.

        Args:
            category (TeacherTypeEnum): відповідна категорія

        Returns:
            List:
                Tuple:
                    int: ID вчителя
                    str: ім'я вчителя
        """
        query = (
            select(TeacherModel.id, TeacherModel.name)
            .join(TeacherQualificationModel, TeacherModel.id == TeacherQualificationModel.teacher_id)
            .where(TeacherQualificationModel.qualification == category)
        )
        result = await self.session.execute(query)
        return [(teacher_id, teacher_name) for teacher_id, teacher_name in result]  # типізація result.all()

    async def get_teacher_by_id(self, teacher_id: int) -> str:
        """
        Повертає ім'я вчителя за його ID.

        Args:
            teacher_id (int): ID вчителя

        Returns:
            str: ім'я вчителя
        """
        query = select(TeacherModel.name).where(
            TeacherModel.id == teacher_id
        )
        result = await self.session.execute(query)
        return result.scalar() or "Невідомий вчитель"

    async def _insert_teacher(self) -> None:
        teachers = [TeacherQualificationModel(teacher_id=tid, qualification=tqual) for tid, tqual in data]
        self.session.add_all(teachers)
        await self.session.commit()
