from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.scheduler.jobs import release_expired_jails, respawn_dead_players


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Asia/Tehran")

    scheduler.add_job(
        respawn_dead_players,
        "interval",
        seconds=30,
        args=[bot],
        id="respawn_dead_players",
        replace_existing=True,
    )
    scheduler.add_job(
        release_expired_jails,
        "interval",
        seconds=30,
        args=[bot],
        id="release_expired_jails",
        replace_existing=True,
    )

    return scheduler
