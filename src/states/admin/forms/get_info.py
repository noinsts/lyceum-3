from aiogram.fsm.state import State, StatesGroup


class GetInfoStates(StatesGroup):
    waiting_for_forms = State()
