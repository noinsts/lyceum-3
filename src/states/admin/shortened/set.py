from aiogram.fsm.state import State, StatesGroup


class SetStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_status = State()
    waiting_for_schedule = State()
    waiting_for_confirmation = State()
