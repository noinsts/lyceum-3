from sqlalchemy import Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .card import CardModel


class UserCardModel(BaseModel):
    __tablename__ = "user_card"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("card.id"), nullable=False)

    card: Mapped["CardModel"] = relationship(back_populates="user_cards")
