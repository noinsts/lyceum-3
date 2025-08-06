from aiogram.fsm.state import State, StatesGroup


class AccessUnblock(StatesGroup):
    waiting_for_type = State()
    waiting_for_user_id = State()
    waiting_for_teacher_name = State()
    waiting_for_confirmation = State()
