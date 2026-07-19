"""
سرویس ردیابی دستاوردها (Achievement)

هر Achievement یه goal_type داره (مثلا attacks_made, kills, tiriak_earned)
این سرویس یه goal_type و مقدار جدید رو می‌گیره، تمام دستاوردهای همون نوع رو چک می‌کنه
و هرکدوم که به هدفش رسیده باشه رو unlock می‌کنه و جایزه میده

برای goal_type هایی که «انباشتی» نیستن (مثل level_reached که یه مقدار لحظه‌ایه نه جمع‌شونده)
مقدار مطلق رو پاس می‌دیم نه افزایشی
"""

from datetime import datetime

from bot.database.db import get_conn
from bot.database.repositories import user_repo
from bot.services.level_service import add_xp_and_check_levelup

# goal_type هایی که مقدار مطلق (نه انباشتی) هستن - یعنی progress = مقدار فعلی، نه جمع
ABSOLUTE_GOAL_TYPES = {
    "level_reached", "tiriak_earned", "bank_saved", "dogs_owned", "weapons_owned",
    "buildings_total_level", "reputation_reached", "max_combo_reached",
    "days_since_join", "days_in_team",
}


async def bump_progress(user_id: int, goal_type: str, amount: int = 1) -> list[dict]:
    """
    پیشرفت رو برای همه دستاوردهای این goal_type آپدیت می‌کنه
    برمی‌گردونه لیست دستاوردهایی که تازه unlock شدن (برای نمایش پیام)
    """
    unlocked = []
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT * FROM achievements_catalog WHERE goal_type = ?", (goal_type,)
        )
        achievements = await cursor.fetchall()

        for ach in achievements:
            cursor = await conn.execute(
                "SELECT * FROM user_achievements WHERE user_id = ? AND achievement_id = ?",
                (user_id, ach["achievement_id"]),
            )
            existing = await cursor.fetchone()

            if existing and existing["unlocked_at"]:
                continue  # قبلا گرفته شده

            if goal_type in ABSOLUTE_GOAL_TYPES:
                new_progress = amount
            else:
                current = existing["progress"] if existing else 0
                new_progress = current + amount

            if existing:
                await conn.execute(
                    "UPDATE user_achievements SET progress = ? WHERE user_id = ? AND achievement_id = ?",
                    (new_progress, user_id, ach["achievement_id"]),
                )
            else:
                await conn.execute(
                    "INSERT INTO user_achievements (user_id, achievement_id, progress) VALUES (?, ?, ?)",
                    (user_id, ach["achievement_id"], new_progress),
                )

            if new_progress >= ach["goal_amount"]:
                await conn.execute(
                    "UPDATE user_achievements SET unlocked_at = ? WHERE user_id = ? AND achievement_id = ?",
                    (datetime.utcnow().isoformat(), user_id, ach["achievement_id"]),
                )
                unlocked.append(dict(ach))

        await conn.commit()

    for ach in unlocked:
        if ach["reward_tiriak"]:
            await user_repo.adjust_tiriak(user_id, ach["reward_tiriak"])
        if ach["reward_diamond"]:
            await user_repo.adjust_diamond(user_id, ach["reward_diamond"])
        if ach["reward_xp"]:
            await add_xp_and_check_levelup(user_id, ach["reward_xp"])

    return unlocked


async def get_user_achievements(user_id: int, only_unlocked: bool = False) -> list[dict]:
    async with get_conn() as conn:
        if only_unlocked:
            cursor = await conn.execute(
                """SELECT ac.*, ua.progress, ua.unlocked_at FROM achievements_catalog ac
                   JOIN user_achievements ua ON ac.achievement_id = ua.achievement_id
                   WHERE ua.user_id = ? AND ua.unlocked_at IS NOT NULL
                   ORDER BY ua.unlocked_at DESC""",
                (user_id,),
            )
        else:
            cursor = await conn.execute(
                """SELECT ac.*, COALESCE(ua.progress, 0) as progress, ua.unlocked_at
                   FROM achievements_catalog ac
                   LEFT JOIN user_achievements ua
                     ON ac.achievement_id = ua.achievement_id AND ua.user_id = ?
                   ORDER BY ac.tier, ac.achievement_id""",
                (user_id,),
            )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_achievement_summary(user_id: int) -> dict:
    all_ach = await get_user_achievements(user_id)
    unlocked_count = sum(1 for a in all_ach if a["unlocked_at"])
    return {"unlocked": unlocked_count, "total": len(all_ach)}
