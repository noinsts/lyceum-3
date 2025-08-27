from aiogram.fsm.state import State, StatesGroup


class TeacherFormStates(StatesGroup):
    waiting_for_form = State()
    waiting_for_category = State()
    waiting_for_name = State()
    waiting_for_confirmation = State()
