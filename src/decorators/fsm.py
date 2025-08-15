from functools import wraps
from typing import Callable

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from src.exceptions import ValidationError


def next_state(state_to_set: State):
    """
    Декоратор змінює FSM стан
    """
    def decorator(handler_func: Callable):
        @wraps(handler_func)
        async def wrapper(self, event: Message | CallbackQuery, state: FSMContext, *args, **kwargs):
            try:
                await handler_func(self, event, state, *args, **kwargs)
                await state.set_state(state_to_set)
            except ValidationError:
                pass
        return wrapper
    return decorator
