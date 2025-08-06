from aiogram.fsm.state import State, StatesGroup


class AccessStatus(StatesGroup):
    waiting_for_type = State()
    waiting_for_user_id = State()
    waiting_for_teacher_name = State()
