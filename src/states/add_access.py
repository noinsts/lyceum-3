from aiogram.fsm.state import State, StatesGroup


class DevAddAccess(StatesGroup):
    waiting_for_data = State()
    waiting_for_confirmation = State()
