from functools import wraps

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.exceptions import ValidationError


def with_validation(validate):
    """
    Декоратор, що валідує message.text за вказаним валідатором
    """
    def decorator(handler_func):
        @wraps(handler_func)
        async def wrapper(self, message: Message, state: FSMContext, *args, **kwargs):
            try:
                validate(message.text)
            except ValidationError as e:
                await message.answer(str(e))
                return
            await handler_func(self, message, state, *args, **kwargs)
        return wrapper
    return decorator
