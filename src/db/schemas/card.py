from pydantic import BaseModel

from src.enums import RarityCardsEnum


class CardSchema(BaseModel):
    name: str
    description: str
    sticker_id: str
    rarity: RarityCardsEnum
