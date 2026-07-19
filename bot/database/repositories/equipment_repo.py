from bot.database.db import get_conn


async def list_equipment_catalog() -> list[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM equipment_catalog")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_user_equipment(user_id: int) -> list[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT ue.*, ec.name_fa, ec.emoji, ec.slot
               FROM user_equipment ue JOIN equipment_catalog ec ON ue.equipment_id = ec.equipment_id
               WHERE ue.user_id = ?""",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def upgrade_equipment(user_id: int, equipment_id: str, new_level: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO user_equipment (user_id, equipment_id, level)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, equipment_id) DO UPDATE SET level = excluded.level""",
            (user_id, equipment_id, new_level),
        )
        await conn.commit()
