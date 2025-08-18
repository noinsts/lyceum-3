from enum import Enum


class RarityCardsEnum(str, Enum):
    DEFAULT = "Звичайна"
    RARE = "Рідкісна"
    SUPERRARE = "Дуже рідкісна"
    EPIC = "Епічна"
    LEGENDARY = "Легендарна"
