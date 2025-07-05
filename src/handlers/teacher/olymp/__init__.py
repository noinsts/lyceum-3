from typing import List

from aiogram import Router

from .hub import OlympHub
from .create import CreateHandler
from .edit import EditOlympHandler
from .list import ListOlympsHandler
from .delete import DeleteOlympHandler


def get_olymp_router() -> List[Router]:
    return [
        OlympHub().get_router(),
        CreateHandler().get_router(),
        EditOlympHandler().get_router(),
        ListOlympsHandler().get_router(),
        DeleteOlympHandler().get_router()
    ]
