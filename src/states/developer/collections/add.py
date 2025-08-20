from aiogram.fsm.state import State, StatesGroup


class AddStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_collection = State()
    waiting_for_sticker = State()
    waiting_for_rarity = State()
    waiting_for_confirmation = State()
