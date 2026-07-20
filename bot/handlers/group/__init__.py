from aiogram import Dispatcher

from bot.handlers.group.attack_handler import router as attack_router
from bot.handlers.group.direct_commands_handler import router as direct_commands_router
from bot.handlers.group.membership_handler import router as membership_router
from bot.handlers.group.start_handler import router as start_router
from bot.handlers.group.theft_handler import router as theft_router


def register_group_handlers(dp: Dispatcher) -> None:
    dp.include_router(membership_router)
    dp.include_router(start_router)
    dp.include_router(direct_commands_router)
    dp.include_router(attack_router)
    dp.include_router(theft_router)
