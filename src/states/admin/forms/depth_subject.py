from aiogram.fsm.state import State, StatesGroup


class DepthSubjectStates(StatesGroup):
    waiting_for_form = State()
    waiting_for_subject = State()
    waiting_for_confirmation = State()
