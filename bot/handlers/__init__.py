from aiogram import Dispatcher

from bot.handlers.admin import register_admin_handlers
from bot.handlers.group import register_group_handlers
from bot.handlers.private import register_private_handlers
from bot.handlers.shared import register_shared_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    # ترتیب مهمه: ادمین قبل از بقیه چک بشه، بعد گروه، بعد پیوی، بعد مشترک
    register_admin_handlers(dp)
    register_group_handlers(dp)
    register_private_handlers(dp)
    register_shared_handlers(dp)
