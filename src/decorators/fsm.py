from functools import wraps

from aiogram.types import Message
from aiogram.fsm.context import FSMContext


def next_state(state_to_set):
    """
    Декоратор змінює FSM стан
    """
    def decorator(handler_func):
        @wraps(handler_func)
        async def wrapper(self, message: Message, state: FSMContext, *args, **kwargs):
            await handler_func(self, message, state, *args, **kwargs)
            await state.set_state(state_to_set)
        return wrapper
    return decorator
