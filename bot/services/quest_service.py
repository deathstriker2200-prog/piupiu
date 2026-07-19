from datetime import datetime, timedelta

from bot.database.repositories import quest_repo, user_repo
from bot.services.level_service import add_xp_and_check_levelup


class QuestError(Exception):
    pass


def period_start(period: str) -> str:
    return _period_start(period)


def _period_start(period: str) -> str:
    now = datetime.utcnow()
    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now
    return start.isoformat()


async def track_progress(user_id: int, goal_type: str, amount: int = 1) -> list[dict]:
    """
    وقتی کاربر کاری انجام میده (حمله، کشتن، غذادادن، خرید، ارتقا) این تابع صدا زده میشه
    پیشرفت کوئست‌های مرتبط رو آپدیت می‌کنه و کوئست‌های تکمیل‌شده رو برمی‌گردونه
    """
    completed = []
    quests = await quest_repo.list_active_quests()
    relevant = [q for q in quests if q.goal_type == goal_type]

    for quest in relevant:
        period_start = _period_start(quest.period)
        await quest_repo.increment_progress(user_id, quest.quest_id, period_start, amount)
        progress = await quest_repo.get_progress(user_id, quest.quest_id, period_start)

        if progress and not progress["is_completed"] and progress["progress"] >= quest.goal_amount:
            await quest_repo.mark_completed(user_id, quest.quest_id, period_start)
            if quest.reward_xp:
                await add_xp_and_check_levelup(user_id, quest.reward_xp)
            if quest.reward_tiriak:
                await user_repo.adjust_tiriak(user_id, quest.reward_tiriak)
            if quest.reward_diamond:
                await user_repo.adjust_diamond(user_id, quest.reward_diamond)
            completed.append(
                {
                    "title": quest.title,
                    "reward_xp": quest.reward_xp,
                    "reward_tiriak": quest.reward_tiriak,
                    "reward_diamond": quest.reward_diamond,
                }
            )

    return completed
