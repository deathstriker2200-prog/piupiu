from typing import Optional

from bot.database.db import get_conn
from bot.database.models.weapon import Weapon


async def get_weapon(weapon_id: str) -> Optional[Weapon]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT * FROM weapons WHERE weapon_id = ?", (weapon_id,)
        )
        row = await cursor.fetchone()
        return Weapon.from_row(row) if row else None


async def list_weapons(category: Optional[str] = None) -> list[Weapon]:
    async with get_conn() as conn:
        if category:
            cursor = await conn.execute(
                "SELECT * FROM weapons WHERE is_active = 1 AND category = ? ORDER BY required_level",
                (category,),
            )
        else:
            cursor = await conn.execute(
                "SELECT * FROM weapons WHERE is_active = 1 ORDER BY category, required_level"
            )
        rows = await cursor.fetchall()
        return [Weapon.from_row(r) for r in rows]


async def user_owns_weapon(user_id: int, weapon_id: str) -> bool:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT 1 FROM user_weapons WHERE user_id = ? AND weapon_id = ?",
            (user_id, weapon_id),
        )
        return (await cursor.fetchone()) is not None


async def get_user_weapons(user_id: int) -> list[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT uw.*, w.name_fa, w.emoji, w.damage, w.category, w.cooldown_sec
               FROM user_weapons uw JOIN weapons w ON uw.weapon_id = w.weapon_id
               WHERE uw.user_id = ?""",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def add_weapon_to_user(user_id: int, weapon_id: str, initial_ammo: int = 0) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT OR IGNORE INTO user_weapons (user_id, weapon_id, ammo_current)
               VALUES (?, ?, ?)""",
            (user_id, weapon_id, initial_ammo),
        )
        await conn.commit()


async def get_equipped_weapon(user_id: int) -> Optional[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT uw.*, w.name_fa, w.emoji, w.damage, w.category, w.cooldown_sec,
                      w.needs_ammo, w.magazine_size, w.reload_sec
               FROM user_weapons uw JOIN weapons w ON uw.weapon_id = w.weapon_id
               WHERE uw.user_id = ? AND uw.is_equipped = 1""",
            (user_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def equip_weapon(user_id: int, weapon_id: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE user_weapons SET is_equipped = 0 WHERE user_id = ?", (user_id,)
        )
        await conn.execute(
            "UPDATE user_weapons SET is_equipped = 1 WHERE user_id = ? AND weapon_id = ?",
            (user_id, weapon_id),
        )
        await conn.commit()


async def set_ammo(user_id: int, weapon_id: str, ammo: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE user_weapons SET ammo_current = ? WHERE user_id = ? AND weapon_id = ?",
            (ammo, user_id, weapon_id),
        )
        await conn.commit()


async def get_ammo_cooldown(user_id: int, weapon_id: str) -> Optional[str]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT available_at FROM ammo_cooldowns WHERE user_id = ? AND weapon_id = ?",
            (user_id, weapon_id),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return row["available_at"]


async def set_ammo_cooldown(user_id: int, weapon_id: str, available_at_iso: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO ammo_cooldowns (user_id, weapon_id, available_at)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, weapon_id) DO UPDATE SET available_at = excluded.available_at""",
            (user_id, weapon_id, available_at_iso),
        )
        await conn.commit()


async def get_cooldown(user_id: int, weapon_id: str) -> Optional[str]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT available_at FROM attack_cooldowns WHERE user_id = ? AND weapon_id = ?",
            (user_id, weapon_id),
        )
        row = await cursor.fetchone()
        return row["available_at"] if row else None


async def set_cooldown(user_id: int, weapon_id: str, available_at_iso: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO attack_cooldowns (user_id, weapon_id, available_at)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, weapon_id) DO UPDATE SET available_at = excluded.available_at""",
            (user_id, weapon_id, available_at_iso),
        )
        await conn.commit()


async def log_attack(
    attacker_id: int,
    target_id: int,
    weapon_id: str,
    damage_dealt: int,
    tiriak_stolen: int,
    target_died: bool,
) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO attack_logs (attacker_id, target_id, weapon_id, damage_dealt, tiriak_stolen, target_died)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (attacker_id, target_id, weapon_id, damage_dealt, tiriak_stolen, 1 if target_died else 0),
        )
        await conn.commit()
