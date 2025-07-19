from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_class = State()
    waiting_for_teacher_name = State()
    waiting_for_student_name = State()
    finally_register = State()


class TeacherTypesStates(StatesGroup):
    choosing_teacher = State()


class StudentOlympsStates(StatesGroup):
    waiting_for_name = State()


class CreateOlympStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_form = State()
    waiting_for_student_name = State()
    waiting_for_olymp_stage = State()
    waiting_for_date = State()
    waiting_for_note = State()
    confirm_creating = State()


class DevAddAccess(StatesGroup):
    waiting_for_data = State()
    waiting_for_confirmation = State()
