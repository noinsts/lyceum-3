from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class TeacherModel(BaseModel):
    __tablename__ = 'teachers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    qualifications = relationship('TeacherQualificationModel', back_populates='teacher')
    verification = relationship("TeacherVerificationModel", uselist=False, back_populates="teacher")
