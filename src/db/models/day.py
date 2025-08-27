import datetime

from sqlalchemy import Date, Integer, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class DayModel(BaseModel):
    __tablename__ = "day"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_shortened: Mapped[bool] = mapped_column(Boolean, nullable=False)
    call_schedule: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, unique=True)
