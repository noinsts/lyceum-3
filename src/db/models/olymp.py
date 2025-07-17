from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class OlympModel(BaseModel):
    __tablename__ = 'olymp'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form: Mapped[str] = mapped_column(String(5), nullable=False)
    student_name: Mapped[str] = mapped_column(String(50), nullable=False)
    teacher_name: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    stage_olymp: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    note: Mapped[str] = mapped_column(String(256), nullable=True)
