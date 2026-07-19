"""
سرویس نشان‌ها (Badge)

برخلاف Achievement که پیشرفت تدریجی داره، Badge بر اساس یه شرط کلی داده میشه
این تابع بعد از رویدادهای مهم (کشتن، خرید، و غیره) صدا زده میشه و شرط‌ها رو چک می‌کنه
"""

from datetime import datetime

from bot.database.db import get_conn
from bot.database.repositories import user_repo
from bot.services.stats_service import get_user_stats


async def _has_badge(conn, user_id: int, badge_id: str) -> bool:
    cursor = await conn.execute(
        "SELECT 1 FROM user_badges WHERE user_id = ? AND badge_id = ?", (user_id, badge_id)
    )
    return (await cursor.fetchone()) is not None


async def _award(conn, user_id: int, badge_id: str) -> None:
    await conn.execute(
        "INSERT OR IGNORE INTO user_badges (user_id, badge_id) VALUES (?, ?)",
        (user_id, badge_id),
    )


async def evaluate_badges(user_id: int) -> list[str]:
    """
    همه شرط‌های نشان رو برای این کاربر چک می‌کنه و هرکدوم که واجد شرایطه رو میده
    برمی‌گردونه لیست badge_id هایی که تازه گرفته شدن
    """
    user = await user_repo.get_user(user_id)
    if user is None:
        return []

    stats = await get_user_stats(user_id)
    newly_awarded = []

    async with get_conn() as conn:
        checks = [
            ("badge_killer", stats["kills"] >= 50),
            ("badge_rich", user.tiriak_point >= 50000),
            ("badge_legend", user.level >= 40),
            ("badge_golden_luck", user.luck >= 90),
            ("badge_veteran", _days_since(user.created_at) >= 60),
            ("badge_boss_hunter", stats.get("boss_participations", 0) >= 10),
        ]

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM user_dogs WHERE user_id = ?", (user_id,)
        )
        dog_count = (await cursor.fetchone())["c"]
        checks.append(("badge_dog_lover", dog_count >= 3))

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM user_weapons WHERE user_id = ?", (user_id,)
        )
        weapon_count = (await cursor.fetchone())["c"]
        cursor = await conn.execute("SELECT COUNT(*) as c FROM weapons WHERE is_active = 1")
        total_weapons = (await cursor.fetchone())["c"]
        checks.append(("badge_collector", total_weapons > 0 and weapon_count >= total_weapons))

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM marketplace_sale_history WHERE seller_id = ?",
            (user_id,),
        )
        sales_count = (await cursor.fetchone())["c"]
        checks.append(("badge_trader", sales_count >= 20))

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM gift_log WHERE sender_id = ?", (user_id,)
        )
        gifts_sent = (await cursor.fetchone())["c"]
        checks.append(("badge_generous", gifts_sent >= 20))

        cursor = await conn.execute(
            "SELECT COUNT(*) as c FROM craft_log WHERE user_id = ?", (user_id,)
        )
        crafts = (await cursor.fetchone())["c"]
        checks.append(("badge_crafter", crafts >= 20))

        cursor = await conn.execute(
            "SELECT team_id FROM team_members WHERE user_id = ? AND role = 'owner'",
            (user_id,),
        )
        is_team_owner = (await cursor.fetchone()) is not None
        checks.append(("badge_team_leader", is_team_owner))

        for badge_id, condition in checks:
            if condition and not await _has_badge(conn, user_id, badge_id):
                await _award(conn, user_id, badge_id)
                newly_awarded.append(badge_id)

        await conn.commit()

    return newly_awarded


def _days_since(iso_date: str) -> int:
    try:
        created_dt = datetime.fromisoformat(iso_date)
        return (datetime.utcnow() - created_dt).days
    except Exception:
        return 0


async def get_user_badges(user_id: int) -> list[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT bc.*, ub.earned_at, ub.is_pinned FROM badges_catalog bc
               JOIN user_badges ub ON bc.badge_id = ub.badge_id
               WHERE ub.user_id = ? ORDER BY ub.earned_at DESC""",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
