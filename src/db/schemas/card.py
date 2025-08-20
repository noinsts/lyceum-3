from typing import Optional

from pydantic import BaseModel

from src.enums import RarityCardsEnum


class CardSchema(BaseModel):
    name: str
    description: str
    collection: Optional[str] = None
    sticker_id: str
    rarity: RarityCardsEnum
