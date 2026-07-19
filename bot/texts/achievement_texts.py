"""متن‌های اعلام دستاورد و نشان جدید"""


def achievement_unlocked(icon: str, title: str, description: str) -> str:
    return f"🏅 دستاورد جدید باز شد\n{icon} {title}\n{description}"


async def badge_earned(badge_id: str) -> str:
    from bot.database.db import get_conn

    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT icon, title, description FROM badges_catalog WHERE badge_id = ?",
            (badge_id,),
        )
        row = await cursor.fetchone()

    if row is None:
        return "🏷 یه نشان جدید گرفتی"

    return f"🏷 نشان جدید گرفتی\n{row['icon']} {row['title']}\n{row['description']}"
