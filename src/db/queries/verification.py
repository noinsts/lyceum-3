from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import TeacherVerificationModel


class TeacherVerificationQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_verif(self, user_id: int, teacher_name: str) -> bool:
        """Повертає булеве значення верифікації вчителя"""
        query = select(TeacherVerificationModel.is_verified).where(
            TeacherVerificationModel.user_id == user_id,
            TeacherVerificationModel.teacher_name == teacher_name,
        )
        result = await self.session.execute(query)
        value = result.scalar()
        return bool(value)

    async def get_name(self, user_id: int) -> str | None:
        """Отримує ім'я вчителя за user_id"""
        query = select(TeacherVerificationModel.teacher_name).where(
            TeacherVerificationModel.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_user_id(self, teacher_name: str) -> int | None:
        """Отримує user_id за іменем вчителя"""
        query = select(TeacherVerificationModel.user_id).where(
            TeacherVerificationModel.teacher_name == teacher_name
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def add_verif_teacher(self, user_id: int, teacher_name: str) -> None:
        """Додає або оновлює верифікацію вчителя"""
        try:
            # спочатку перевіряємо чи існує запис
            query = select(TeacherVerificationModel.teacher_name).where(
                TeacherVerificationModel.user_id == user_id
            )
            result = await self.session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                # оновлюємо існуючий запис
                update_query = update(TeacherVerificationModel).where(
                    TeacherVerificationModel.user_id == user_id
                ).values(
                    teacher_name=teacher_name,
                    is_verified=True
                )
                await self.session.execute(update_query)
            else:
                # створюємо новий запис
                new_verification = TeacherVerificationModel(
                    user_id=user_id,
                    teacher_name=teacher_name,
                    is_verified=True
                )
                self.session.add(new_verification)

            await self.session.commit()

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
