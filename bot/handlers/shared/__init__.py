from aiogram import Dispatcher

from bot.handlers.shared.achievement_handler import router as achievement_router
from bot.handlers.shared.daily_login_handler import router as daily_login_router
from bot.handlers.shared.help_handler import router as help_router


def register_shared_handlers(dp: Dispatcher) -> None:
    dp.include_router(help_router)
    dp.include_router(achievement_router)
    dp.include_router(daily_login_router)
