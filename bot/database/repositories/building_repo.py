from typing import Optional

from bot.database.db import get_conn
from bot.database.models.building import BuildingType


async def list_building_types() -> list[BuildingType]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM buildings_catalog")
        rows = await cursor.fetchall()
        return [BuildingType.from_row(r) for r in rows]


async def get_building_type(building_id: str) -> Optional[BuildingType]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT * FROM buildings_catalog WHERE building_id = ?", (building_id,)
        )
        row = await cursor.fetchone()
        return BuildingType.from_row(row) if row else None


async def get_user_buildings(user_id: int) -> list[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT ub.*, bc.name_fa, bc.emoji, bc.effect_type, bc.base_value, bc.value_growth
               FROM user_buildings ub JOIN buildings_catalog bc ON ub.building_id = bc.building_id
               WHERE ub.user_id = ?""",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_user_building(user_id: int, building_id: str) -> Optional[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT ub.*, bc.name_fa, bc.emoji, bc.effect_type, bc.base_value, bc.value_growth
               FROM user_buildings ub JOIN buildings_catalog bc ON ub.building_id = bc.building_id
               WHERE ub.user_id = ? AND ub.building_id = ?""",
            (user_id, building_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def upgrade_building(user_id: int, building_id: str, new_level: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO user_buildings (user_id, building_id, level)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, building_id) DO UPDATE SET level = excluded.level""",
            (user_id, building_id, new_level),
        )
        await conn.commit()


async def mark_collected(user_id: int, building_id: str, collected_at_iso: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE user_buildings SET last_collected_at = ? WHERE user_id = ? AND building_id = ?",
            (collected_at_iso, user_id, building_id),
        )
        await conn.commit()
