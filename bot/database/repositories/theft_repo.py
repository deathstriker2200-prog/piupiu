from bot.database.db import get_conn


async def log_theft(thief_id: int, target_id: int, success: bool, amount_stolen: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO theft_logs (thief_id, target_id, success, amount_stolen)
               VALUES (?, ?, ?, ?)""",
            (thief_id, target_id, 1 if success else 0, amount_stolen),
        )
        await conn.commit()
