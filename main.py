import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config.settings import settings
from bot.database.db import init_db
from bot.handlers import register_all_handlers
from bot.middlewares import register_all_middlewares
from bot.scheduler.scheduler import setup_scheduler


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    log = logging.getLogger("tiryaki")

    log.info("در حال راه‌اندازی دیتابیس ...")
    await init_db(settings.db_path)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    register_all_middlewares(dp)
    register_all_handlers(dp)

    scheduler = setup_scheduler(bot)
    scheduler.start()

    log.info("ربات تریاکی پیو پیو روشن شد 🔥")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
