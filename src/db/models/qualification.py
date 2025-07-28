from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy import ForeignKey

from .base import BaseModel
from src.enums import TeacherTypeEnum


class TeacherQualificationModel(BaseModel):
    __tablename__ = 'teacher_qualification'

    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey('teachers.id'), primary_key=True)
    qualification: Mapped[TeacherTypeEnum] = mapped_column(
        PgEnum(TeacherTypeEnum, name='qualification_enum'),
        primary_key=True
    )

    teacher = relationship('TeacherModel', back_populates='qualifications')
