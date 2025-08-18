from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from .base import BaseModel
from src.enums import RarityCardsEnum


class CardModel(BaseModel):
    __tablename__ = "card"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    sticker_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    rarity: Mapped[RarityCardsEnum] = mapped_column(
        PgEnum(RarityCardsEnum, name="rarity_card_enum"), nullable=False
    )
