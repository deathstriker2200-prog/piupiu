import logging
from datetime import datetime

from aiogram import Bot

from bot.database.db import get_conn
from bot.services.combat_service import try_respawn_if_ready
from bot.services.theft_service import try_release_if_ready
from bot.texts.battle_texts import respawned

log = logging.getLogger("tiryaki.scheduler")


async def respawn_dead_players(bot: Bot) -> None:
    """هر ۳۰ ثانیه چک می‌کنه کدوم بازیکن‌های مرده باید respawn بشن
    پیام respawn رو تو آخرین گروهی که خود کاربر توش فعال بوده می‌فرسته
    (ربات به یه گروه ثابت وابسته نیست، تو هر گروهی که اضافه بشه کار می‌کنه)"""
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT user_id, full_name, died_at, last_active_group_id FROM users "
            "WHERE is_dead = 1 AND died_at IS NOT NULL"
        )
        rows = await cursor.fetchall()

    for row in rows:
        did_respawn = await try_respawn_if_ready(row["user_id"])
        if did_respawn and row["last_active_group_id"]:
            try:
                await bot.send_message(
                    row["last_active_group_id"], respawned(row["full_name"] or "بازیکن")
                )
            except Exception:
                log.exception("failed to send respawn message for user %s", row["user_id"])


async def release_expired_jails(bot: Bot) -> None:
    """هر ۳۰ ثانیه چک می‌کنه کدوم بازیکن‌های زندانی باید آزاد بشن"""
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT user_id FROM users WHERE jailed_until IS NOT NULL"
        )
        rows = await cursor.fetchall()

    for row in rows:
        await try_release_if_ready(row["user_id"])
