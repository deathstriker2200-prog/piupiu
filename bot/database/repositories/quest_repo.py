from typing import Optional

from bot.database.db import get_conn
from bot.database.models.quest import Quest


async def list_active_quests(period: Optional[str] = None) -> list[Quest]:
    async with get_conn() as conn:
        if period:
            cursor = await conn.execute(
                "SELECT * FROM quests WHERE is_active = 1 AND period = ?", (period,)
            )
        else:
            cursor = await conn.execute("SELECT * FROM quests WHERE is_active = 1")
        rows = await cursor.fetchall()
        return [Quest.from_row(r) for r in rows]


async def create_quest(
    title: str,
    period: str,
    goal_type: str,
    goal_amount: int,
    reward_xp: int,
    reward_tiriak: int,
    reward_diamond: int,
) -> int:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """INSERT INTO quests (title, period, goal_type, goal_amount, reward_xp, reward_tiriak, reward_diamond)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, period, goal_type, goal_amount, reward_xp, reward_tiriak, reward_diamond),
        )
        await conn.commit()
        return cursor.lastrowid


async def get_progress(user_id: int, quest_id: int, period_start: str) -> Optional[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT * FROM user_quest_progress
               WHERE user_id = ? AND quest_id = ? AND period_start = ?""",
            (user_id, quest_id, period_start),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def increment_progress(
    user_id: int, quest_id: int, period_start: str, amount: int = 1
) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO user_quest_progress (user_id, quest_id, progress, period_start)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, quest_id, period_start)
               DO UPDATE SET progress = progress + excluded.progress""",
            (user_id, quest_id, amount, period_start),
        )
        await conn.commit()


async def mark_completed(user_id: int, quest_id: int, period_start: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """UPDATE user_quest_progress SET is_completed = 1
               WHERE user_id = ? AND quest_id = ? AND period_start = ?""",
            (user_id, quest_id, period_start),
        )
        await conn.commit()
