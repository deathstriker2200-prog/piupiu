"""
سرویس ورود روزانه (Daily Login)

هر روز یه بار می‌تونی جایزه بگیری
اگه پشت سر هم بیای، Streak بالا میره و جایزه بیشتر میشه
اگه یه روز رو جا بندازی، Streak صفر میشه مگه اینکه آیتم Freeze داشته باشی
"""

from datetime import datetime

from bot.database.db import get_conn
from bot.database.repositories import user_repo
from bot.services.level_service import add_xp_and_check_levelup

STREAK_MILESTONES = [
    (1, 50, 0),
    (3, 100, 0),
    (7, 200, 100),   # 1 الماس قدیمی = 100 تریاک‌پوینت (الماس حذف شده)
    (14, 350, 200),
    (30, 800, 500),
]
BASE_REWARD_TIRIAK = 30
BASE_REWARD_XP = 10


class DailyLoginError(Exception):
    pass


def _reward_for_streak(streak: int) -> tuple:
    """برمی‌گردونه (تریاک‌پوینت, الماس) بر اساس روز فعلی streak - الماس حذف شده پس همیشه صفره"""
    tiriak = BASE_REWARD_TIRIAK + streak * 15
    bonus_tiriak = 0
    for milestone_day, _, milestone_bonus in STREAK_MILESTONES:
        if streak >= milestone_day:
            bonus_tiriak = milestone_bonus
    tiriak += bonus_tiriak
    diamond = 0  # سیستم الماس کاملاً حذف شده
    return tiriak, diamond


async def claim_daily(user_id: int) -> dict:
    user = await user_repo.get_user(user_id)
    if user is None:
        raise DailyLoginError("user_not_found")

    now = datetime.utcnow()
    today_str = now.date().isoformat()

    if user.last_login_at:
        last_dt = datetime.fromisoformat(user.last_login_at)
        if last_dt.date().isoformat() == today_str:
            raise DailyLoginError("already_claimed_today")

        days_gap = (now.date() - last_dt.date()).days
        if days_gap == 1:
            new_streak = user.login_streak + 1
            used_freeze = False
        elif days_gap > 1 and user.streak_freeze_available > 0:
            new_streak = user.login_streak + 1
            used_freeze = True
        else:
            new_streak = 1
            used_freeze = False
    else:
        new_streak = 1
        used_freeze = False

    tiriak_reward, diamond_reward = _reward_for_streak(new_streak)

    async with get_conn() as conn:
        if used_freeze:
            await conn.execute(
                "UPDATE users SET streak_freeze_available = streak_freeze_available - 1 WHERE user_id = ?",
                (user_id,),
            )
        await conn.execute(
            "UPDATE users SET login_streak = ?, last_login_at = ? WHERE user_id = ?",
            (new_streak, now.isoformat(), user_id),
        )
        await conn.commit()

    await user_repo.adjust_tiriak(user_id, tiriak_reward)
    if diamond_reward:
        await user_repo.adjust_diamond(user_id, diamond_reward)
    await add_xp_and_check_levelup(user_id, BASE_REWARD_XP)

    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO daily_login_log (user_id, streak_at_claim, reward_tiriak, reward_diamond, used_freeze)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, new_streak, tiriak_reward, diamond_reward, 1 if used_freeze else 0),
        )
        await conn.commit()

    return {
        "streak": new_streak,
        "reward_tiriak": tiriak_reward,
        "reward_diamond": diamond_reward,
        "reward_xp": BASE_REWARD_XP,
        "used_freeze": used_freeze,
    }


async def grant_streak_freeze(user_id: int, quantity: int = 1) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET streak_freeze_available = streak_freeze_available + ? WHERE user_id = ?",
            (quantity, user_id),
        )
        await conn.commit()
