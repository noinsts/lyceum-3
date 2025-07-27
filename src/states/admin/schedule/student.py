from aiogram.fsm.state import State, StatesGroup


class StudentSchedule(StatesGroup):
    waiting_for_forms = State()
    waiting_for_confirmation = State()

