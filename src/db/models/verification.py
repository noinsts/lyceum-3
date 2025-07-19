from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class TeacherVerificationModel(BaseModel):
    __tablename__ = 'teacher_verification'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_name: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
