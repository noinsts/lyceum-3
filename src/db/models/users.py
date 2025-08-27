from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from .base import BaseModel
from src.enums import DBUserType


class UserModel(BaseModel):
    __tablename__ = 'user'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    user_type: Mapped[DBUserType] = mapped_column(
        PgEnum(DBUserType, name="user_type_enum"), 
        nullable=False
    )
    form: Mapped[str] = mapped_column(String(5), nullable=True)
    teacher_name: Mapped[str] = mapped_column(String(50), nullable=True)
    student_name: Mapped[str] = mapped_column(String(50), nullable=True)
