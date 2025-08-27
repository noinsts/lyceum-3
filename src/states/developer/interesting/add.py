from aiogram.fsm.state import State, StatesGroup


class AddStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_date = State()
    waiting_for_confirmation = State()
