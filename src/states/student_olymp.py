from aiogram.fsm.state import State, StatesGroup

class StudentOlympsStates(StatesGroup):
    waiting_for_name = State()
