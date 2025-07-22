from aiogram.fsm.state import State, StatesGroup


class CreateOlympStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_form = State()
    waiting_for_student_name = State()
    waiting_for_olymp_stage = State()
    waiting_for_date = State()
    waiting_for_note = State()
    confirm_creating = State()
