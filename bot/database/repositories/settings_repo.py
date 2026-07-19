from typing import Optional

from bot.database.db import get_conn


async def get_override(key: str) -> Optional[str]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT value FROM settings_overrides WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        return row["value"] if row else None


async def set_override(key: str, value: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO settings_overrides (key, value, updated_at)
               VALUES (?, ?, datetime('now'))
               ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = datetime('now')""",
            (key, value),
        )
        await conn.commit()


async def get_all_overrides() -> dict:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT key, value FROM settings_overrides")
        rows = await cursor.fetchall()
        return {r["key"]: r["value"] for r in rows}
