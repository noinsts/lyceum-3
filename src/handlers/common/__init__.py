from aiogram import Router

from .start import StartHandler
from .help import HelpHandler
from .register import RegisterHandler


def get_common_router() -> Router:
    "Повернення роутера common handlers"""
    router = Router(name="common")

    routers = [
        StartHandler().get_router(),
        HelpHandler().get_router(),
        RegisterHandler().get_router()
    ]

    for r in routers:
        router.include_router(r)

    return router
