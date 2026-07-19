from aiogram import Dispatcher

from bot.handlers.admin.backup_handler import router as backup_router
from bot.handlers.admin.panel_handler import router as panel_router


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.include_router(backup_router)
    dp.include_router(panel_router)
