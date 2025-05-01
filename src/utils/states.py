from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_class = State()
    waiting_for_teacher_name = State()
    finally_register = State()
