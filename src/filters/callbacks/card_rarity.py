from aiogram.filters.callback_data import CallbackData


class CardRarityCallback(CallbackData, prefix="card_rarity"):
    rarity: str
