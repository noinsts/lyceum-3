from typing import List, cast

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import UserModel
from src.utils import setup_logger
from src.enums import DBUserType
from ..schemas import AddUserSchema

logger = setup_logger()


class RegisterQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_exists(self, user_id: int) -> bool:
        query = select(exists().where(UserModel.user_id == user_id))
        result = await self.session.execute(query)
        return result.scalar()

    async def get_user_type(self, user_id: int) -> DBUserType:
        query = select(UserModel.user_type).where(
            UserModel.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_form(self, user_id: int) -> str | None:
        query = select(UserModel.form).where(
            UserModel.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_teacher_name(self, user_id: int) -> str | None:
        query = select(UserModel.teacher_name).where(
            UserModel.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_student_name(self, user_id: int) -> str | None:
        query = select(UserModel.student_name).where(
            UserModel.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_username(self, user_id: int) -> str | None:
        query = select(UserModel.username).where(
            UserModel.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_full_name(self, user_id: int) -> str | None:
        query = select(UserModel.full_name).where(
            UserModel.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()
    
    async def clone_teacher(self, teacher_name: str) -> bool:
        """Перевіряє чи існує вчитель з таким ім'ям"""
        query = select(UserModel.teacher_name).where(
            UserModel.teacher_name == teacher_name
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def add_user(self, data: AddUserSchema) -> None:
        try:
            if data.user_id is None:
                raise ValueError("user_id є обов'язковим для add_user")

            existing_user = await self.session.get(UserModel, data.user_id)

            user_data = data.model_dump()

            if existing_user:
                for key, value in user_data.items():
                    setattr(existing_user, key, value)
            else:
                self.session.add(UserModel(**user_data))

            await self.session.commit()

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Помилка SQLAlchemy під час add_user в RegisterQueries: {e}")
            raise e
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Інша помилка у add_user: {e}")
            raise

    async def get_by_form(self, form: str) -> List[int]:
        """Повертає список Telegram ID користувачів, у яких вказано задане ім'я вчителя."""
        query = select(UserModel.user_id).where(
            UserModel.form == form
        )
        result = await self.session.execute(query)
        user_ids = result.scalars().all()
        return list(user_ids)
