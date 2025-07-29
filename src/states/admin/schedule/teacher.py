from aiogram.fsm.state import State, StatesGroup


class TeacherSchedule(StatesGroup):
    waiting_for_category = State()
    waiting_for_names = State()
    waiting_for_confirmation = State()
