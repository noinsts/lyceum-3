from aiogram.fsm.state import State, StatesGroup


class GetStates(StatesGroup):
    waiting_for_date = State()
