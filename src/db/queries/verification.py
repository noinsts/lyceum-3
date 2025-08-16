from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import TeacherVerificationModel, TeacherModel


class TeacherVerificationQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_teacher_id(self, teacher_name: str) -> Optional[int]:
        """Внутрішній метод: отримує teacher_id за іменем"""
        query = select(TeacherModel.id).where(TeacherModel.name == teacher_name)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_teacher_name_by_id(self, teacher_id: int) -> str:
        """Метод повертає ім'я вчителя за його ID"""
        query = select(TeacherModel.name).where(TeacherModel.id == teacher_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def is_verif(self, user_id: int, teacher_name: str) -> bool:
        """Повертає булеве значення верифікації вчителя"""
        teacher_id = await self.get_teacher_id(teacher_name)

        if teacher_id is None:
            return False

        query = select(TeacherVerificationModel.is_verified).where(
            TeacherVerificationModel.user_id == user_id,
            TeacherVerificationModel.teacher_id == teacher_id,
        )
        result = await self.session.execute(query)
        value = result.scalar()
        return bool(value)

    async def get_name(self, user_id: int) -> Optional[str]:
        """Отримує ім'я вчителя за user_id"""
        query = (
            select(TeacherModel.name)
            .join(TeacherVerificationModel, TeacherModel.id == TeacherVerificationModel.teacher_id)
            .where(TeacherVerificationModel.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_user_id(self, teacher_name: str) -> Optional[int]:
        """Отримує user_id за іменем вчителя"""
        teacher_id = await self.get_teacher_id(teacher_name)

        if teacher_id is None:
            return None

        query = select(TeacherVerificationModel.user_id).where(
            TeacherVerificationModel.teacher_id == teacher_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_teacher_name(self, user_id: int) -> Optional[str]:
        """Отримує ім'я вчителя за user_id"""
        query = select(TeacherVerificationModel.teacher_id).where(
            TeacherVerificationModel.user_id == user_id
        )
        result = await self.session.execute(query)
        teacher_id = result.scalar()

        if teacher_id is None:
            return None

        teacher_name = await self.get_teacher_name_by_id(teacher_id)
        return teacher_name

    async def add_verif_teacher(self, user_id: int, teacher_name: str) -> None:
        """Додає або оновлює верифікацію вчителя"""
        try:
            teacher_id = await self.get_teacher_id(teacher_name)

            if teacher_id is None:
                raise ValueError(f"Teacher '{teacher_name}' не знайдено в базі.")

            check_query = select(TeacherVerificationModel.user_id).where(
                TeacherVerificationModel.teacher_id == teacher_id
            )
            result = await self.session.execute(check_query)
            existing_user_id = result.scalar_one_or_none()

            if existing_user_id and existing_user_id != user_id:
                raise ValueError(f"Вчитель '{teacher_name}' вже прив'заний до іншого користувачу.")

            existing_query = select(TeacherVerificationModel).where(
                TeacherVerificationModel.user_id == user_id
            )
            result = await self.session.execute(existing_query)
            existing = result.scalar_one_or_none()

            if existing:
                await self.session.execute(update(TeacherVerificationModel).where(
                    TeacherVerificationModel.user_id == user_id
                ).values(
                    teacher_id=teacher_id,
                    is_verified=True
                ))
            else:
                new_verif = TeacherVerificationModel(
                    user_id=user_id,
                    teacher_id=teacher_id,
                    is_verified=True
                )
                self.session.add(new_verif)

            await self.session.commit()

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def set_access(self, user_id: int, verif: bool) -> None:
        """Метод встановлює доступ відповідному акаунту"""
        try:
            query = (
                update(TeacherVerificationModel)
                .where(TeacherVerificationModel.user_id == user_id)
                .values(is_verified=verif)
            )
            await self.session.execute(query)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
