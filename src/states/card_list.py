from aiogram.fsm.state import State, StatesGroup


class CardListStates(StatesGroup):
    waiting_for_actions = State()
