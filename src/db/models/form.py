from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from .base import BaseModel
from src.enums import DepthSubjectEnum


class FormModel(BaseModel):
    __tablename__ = 'form'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey('teachers.id'), unique=True, nullable=True)
    depth_subject: Mapped[DepthSubjectEnum] = mapped_column(
        PgEnum(DepthSubjectEnum, name='depth_subject_enum'),
        nullable=True
    )

    teacher = relationship('TeacherModel', back_populates='form')
