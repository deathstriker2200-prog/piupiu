"""
سیستم کمبو (Combo)

اگه بازیکن پشت سر هم حمله‌های موفق (غیر از Miss/Block) بزنه، Combo بالا میره
Combo x3, x5, x10 سطح‌های مشخصی هستن که پاداش دمیج/XP بیشتری میدن
اگه بین دو حمله بیش از COMBO_TIMEOUT_MINUTES بگذره، Combo صفر میشه
"""

from datetime import datetime, timedelta
from typing import Optional

from bot.database.db import get_conn

COMBO_TIMEOUT_MINUTES = 10

# سطح‌های کمبو: (حداقل تعداد پشت‌سرهم, ضریب دمیج, ضریب XP)
COMBO_TIERS = [
    (10, 1.5, 2.0),
    (5, 1.3, 1.6),
    (3, 1.15, 1.3),
]


def combo_tier_for_count(count: int) -> Optional[tuple]:
    for threshold, dmg_mult, xp_mult in COMBO_TIERS:
        if count >= threshold:
            return threshold, dmg_mult, xp_mult
    return None


async def register_hit(user_id: int, was_successful: bool) -> int:
    """
    بعد از هر حمله صدا زده میشه
    اگه حمله موفق بود (Miss/Block نبود) کمبو رو یکی زیاد می‌کنه، وگرنه صفرش می‌کنه
    برمی‌گردونه مقدار کمبو فعلی بعد این حمله
    """
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT combo_count, combo_updated_at FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return 0

        current_combo = row["combo_count"]
        last_update = row["combo_updated_at"]

        if last_update:
            last_dt = datetime.fromisoformat(last_update)
            if datetime.utcnow() - last_dt > timedelta(minutes=COMBO_TIMEOUT_MINUTES):
                current_combo = 0

        if was_successful:
            new_combo = current_combo + 1
        else:
            new_combo = 0

        await conn.execute(
            "UPDATE users SET combo_count = ?, combo_updated_at = ? WHERE user_id = ?",
            (new_combo, datetime.utcnow().isoformat(), user_id),
        )
        await conn.commit()
        return new_combo


async def get_combo(user_id: int) -> int:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT combo_count, combo_updated_at FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return 0
        if row["combo_updated_at"]:
            last_dt = datetime.fromisoformat(row["combo_updated_at"])
            if datetime.utcnow() - last_dt > timedelta(minutes=COMBO_TIMEOUT_MINUTES):
                return 0
        return row["combo_count"]
