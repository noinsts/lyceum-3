from aiogram.fsm.state import State, StatesGroup


class BrokerStates(StatesGroup):
    waiting_for_type = State()

    waiting_for_form = State()
    waiting_for_continue_form = State()

    waiting_for_teacher_category = State()
    waiting_for_teacher_name = State()
    waiting_for_continue_teacher_name = State()

    waiting_for_message = State()
    waiting_for_confirmation = State()
