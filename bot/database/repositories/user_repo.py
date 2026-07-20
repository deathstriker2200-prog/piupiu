from typing import Optional

from bot.config.game_config import STARTING_HP, STARTING_LEVEL, STARTING_TIRIAK_POINT
from bot.database.db import get_conn
from bot.database.models.user import User


async def get_or_create_user(user_id: int, username: Optional[str], full_name: Optional[str]) -> User:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row is None:
            await conn.execute(
                """INSERT INTO users (user_id, username, full_name, hp, max_hp, level, xp, tiriak_point)
                   VALUES (?, ?, ?, ?, ?, ?, 0, ?)""",
                (user_id, username, full_name, STARTING_HP, STARTING_HP, STARTING_LEVEL, STARTING_TIRIAK_POINT),
            )
            await conn.execute(
                "INSERT INTO bank_accounts (user_id, balance) VALUES (?, 0)", (user_id,)
            )
            # سلاح شروع: مشت (همیشگی رایگان) + آب‌پاش (سلاح پیش‌فرض تجهیزشده برای بازیکن تازه)
            await conn.execute(
                "INSERT OR IGNORE INTO user_weapons (user_id, weapon_id, is_equipped) VALUES (?, 'fist', 0)",
                (user_id,),
            )
            await conn.execute(
                "INSERT OR IGNORE INTO user_weapons (user_id, weapon_id, is_equipped) VALUES (?, 'water_gun', 1)",
                (user_id,),
            )
            await conn.commit()
            cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
        else:
            # همیشه یوزرنیم رو تازه نگه دار
            await conn.execute(
                "UPDATE users SET username = ?, full_name = ?, last_active_at = datetime('now') WHERE user_id = ?",
                (username, full_name, user_id),
            )
            await conn.commit()
        return User.from_row(row)


async def get_user(user_id: int) -> Optional[User]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return User.from_row(row) if row else None


async def update_hp(user_id: int, new_hp: int) -> None:
    async with get_conn() as conn:
        await conn.execute("UPDATE users SET hp = ? WHERE user_id = ?", (max(new_hp, 0), user_id))
        await conn.commit()


async def set_dead(user_id: int, died_at_iso: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET is_dead = 1, hp = 0, died_at = ? WHERE user_id = ?",
            (died_at_iso, user_id),
        )
        await conn.commit()


async def respawn(user_id: int) -> None:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT max_hp FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        max_hp = row["max_hp"] if row else 100
        await conn.execute(
            "UPDATE users SET is_dead = 0, hp = ?, died_at = NULL WHERE user_id = ?",
            (max_hp, user_id),
        )
        await conn.commit()


async def adjust_tiriak(user_id: int, delta: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET tiriak_point = MAX(tiriak_point + ?, 0) WHERE user_id = ?",
            (delta, user_id),
        )
        await conn.commit()


async def adjust_diamond(user_id: int, delta: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET diamond = MAX(diamond + ?, 0) WHERE user_id = ?",
            (delta, user_id),
        )
        await conn.commit()


async def adjust_xp(user_id: int, delta: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET xp = MAX(xp + ?, 0) WHERE user_id = ?", (delta, user_id)
        )
        await conn.commit()


async def set_level(user_id: int, level: int, new_max_hp: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET level = ?, max_hp = ? WHERE user_id = ?",
            (level, new_max_hp, user_id),
        )
        await conn.commit()


async def increment_kills(user_id: int) -> None:
    async with get_conn() as conn:
        await conn.execute("UPDATE users SET kills = kills + 1 WHERE user_id = ?", (user_id,))
        await conn.commit()


async def set_jailed_until(user_id: int, until_iso: Optional[str]) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET jailed_until = ? WHERE user_id = ?", (until_iso, user_id)
        )
        await conn.commit()


async def set_banned(user_id: int, banned: bool) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET is_banned = ? WHERE user_id = ?", (1 if banned else 0, user_id)
        )
        await conn.commit()


async def set_last_active_group(user_id: int, group_chat_id: int) -> None:
    """آخرین گروهی که کاربر توش فعالیت داشته رو ثبت می‌کنه
    این جایگزین یه GROUP_ID ثابت میشه چون ربات باید تو هر گروهی که اضافه بشه کار کنه"""
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET last_active_group_id = ? WHERE user_id = ?",
            (group_chat_id, user_id),
        )
        await conn.commit()


async def get_leaderboard(order_by: str, limit: int = 10) -> list[User]:
    """order_by باید یکی از: level, xp, tiriak_point, kills باشه"""
    allowed = {"level", "xp", "tiriak_point", "kills"}
    if order_by not in allowed:
        raise ValueError(f"invalid order_by: {order_by}")
    async with get_conn() as conn:
        cursor = await conn.execute(
            f"SELECT * FROM users WHERE is_banned = 0 ORDER BY {order_by} DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [User.from_row(r) for r in rows]
