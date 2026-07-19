"""
سرویس متن‌های متنوع حمله هر سلاح

هر سلاح حداقل ۱۰ متن مختلف داره (weapon_attack_lines)
این سرویس یه متن تصادفی انتخاب می‌کنه که اخیراً برای همون کاربر و همون سلاح تکرار نشده باشه
تعداد کمی از آخرین متن‌های استفاده‌شده رو نگه می‌داریم (RECENT_HISTORY_SIZE)
"""

import random

from bot.database.db import get_conn

RECENT_HISTORY_SIZE = 4  # به این تعداد از متن‌های اخیر رو تکرار نکن


async def get_varied_attack_line(user_id: int, weapon_id: str, attacker: str, target: str, damage: int) -> str:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT id, line_text FROM weapon_attack_lines WHERE weapon_id = ?", (weapon_id,)
        )
        all_lines = await cursor.fetchall()

        if not all_lines:
            return f"{attacker} با سلاحش زد تو {target}"

        cursor = await conn.execute(
            """SELECT line_id FROM user_recent_attack_lines
               WHERE user_id = ? AND weapon_id = ?
               ORDER BY used_at DESC LIMIT ?""",
            (user_id, weapon_id, RECENT_HISTORY_SIZE),
        )
        recent_rows = await cursor.fetchall()
        recent_ids = {r["line_id"] for r in recent_rows}

        available = [row for row in all_lines if row["id"] not in recent_ids]
        if not available:
            available = list(all_lines)  # اگه همه تکراری شدن، محدودیت رو موقتا نادیده بگیر

        chosen = random.choice(available)

        await conn.execute(
            "INSERT INTO user_recent_attack_lines (user_id, weapon_id, line_id) VALUES (?, ?, ?)",
            (user_id, weapon_id, chosen["id"]),
        )
        # فقط آخرین چند تا رو نگه دار، بقیه رو پاک کن که جدول بزرگ نشه
        await conn.execute(
            """DELETE FROM user_recent_attack_lines
               WHERE user_id = ? AND weapon_id = ? AND line_id NOT IN (
                   SELECT line_id FROM user_recent_attack_lines
                   WHERE user_id = ? AND weapon_id = ?
                   ORDER BY used_at DESC LIMIT ?
               )""",
            (user_id, weapon_id, user_id, weapon_id, RECENT_HISTORY_SIZE),
        )
        await conn.commit()

    return chosen["line_text"].format(attacker=attacker, target=target, damage=damage)
