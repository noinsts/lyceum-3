import datetime

from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class InterestingModel(BaseModel):
    __tablename__ = "interesting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prompt: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
