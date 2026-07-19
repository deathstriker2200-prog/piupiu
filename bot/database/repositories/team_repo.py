from typing import Optional

from bot.database.db import get_conn
from bot.database.models.team import Team


async def create_team(name: str, owner_id: int, logo_emoji: Optional[str], description: Optional[str]) -> int:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """INSERT INTO teams (name, logo_emoji, description, owner_id)
               VALUES (?, ?, ?, ?)""",
            (name, logo_emoji, description, owner_id),
        )
        team_id = cursor.lastrowid
        await conn.execute(
            "INSERT INTO team_members (team_id, user_id, role) VALUES (?, ?, 'owner')",
            (team_id, owner_id),
        )
        for upgrade_type in ("damage", "hp", "income", "capacity"):
            await conn.execute(
                "INSERT INTO team_upgrades (team_id, upgrade_type, level) VALUES (?, ?, 0)",
                (team_id, upgrade_type),
            )
        await conn.commit()
        return team_id


async def get_team(team_id: int) -> Optional[Team]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM teams WHERE team_id = ?", (team_id,))
        row = await cursor.fetchone()
        return Team.from_row(row) if row else None


async def get_team_by_name(name: str) -> Optional[Team]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM teams WHERE name = ?", (name,))
        row = await cursor.fetchone()
        return Team.from_row(row) if row else None


async def get_user_team(user_id: int) -> Optional[Team]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT t.* FROM teams t JOIN team_members tm ON t.team_id = tm.team_id
               WHERE tm.user_id = ?""",
            (user_id,),
        )
        row = await cursor.fetchone()
        return Team.from_row(row) if row else None


async def get_team_members(team_id: int) -> list[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT tm.*, u.username, u.full_name, u.level FROM team_members tm
               JOIN users u ON tm.user_id = u.user_id WHERE tm.team_id = ?""",
            (team_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def add_member(team_id: int, user_id: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO team_members (team_id, user_id, role) VALUES (?, ?, 'member')",
            (team_id, user_id),
        )
        await conn.commit()


async def remove_member(team_id: int, user_id: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "DELETE FROM team_members WHERE team_id = ? AND user_id = ?", (team_id, user_id)
        )
        await conn.commit()


async def create_join_request(team_id: int, user_id: int) -> int:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "INSERT INTO team_join_requests (team_id, user_id) VALUES (?, ?)",
            (team_id, user_id),
        )
        await conn.commit()
        return cursor.lastrowid


async def get_join_request(request_id: int) -> Optional[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT * FROM team_join_requests WHERE id = ?", (request_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def update_join_request_status(request_id: int, status: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE team_join_requests SET status = ? WHERE id = ?", (status, request_id)
        )
        await conn.commit()


async def get_team_upgrade_level(team_id: int, upgrade_type: str) -> int:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT level FROM team_upgrades WHERE team_id = ? AND upgrade_type = ?",
            (team_id, upgrade_type),
        )
        row = await cursor.fetchone()
        return row["level"] if row else 0


async def set_team_upgrade_level(team_id: int, upgrade_type: str, level: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO team_upgrades (team_id, upgrade_type, level) VALUES (?, ?, ?)
               ON CONFLICT(team_id, upgrade_type) DO UPDATE SET level = excluded.level""",
            (team_id, upgrade_type, level),
        )
        await conn.commit()


async def get_leaderboard_teams(limit: int = 10) -> list[dict]:
    """بر اساس مجموع لول اعضا رتبه‌بندی می‌کنه"""
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT t.team_id, t.name, t.logo_emoji, COALESCE(SUM(u.level), 0) AS total_level
               FROM teams t
               LEFT JOIN team_members tm ON t.team_id = tm.team_id
               LEFT JOIN users u ON tm.user_id = u.user_id
               GROUP BY t.team_id ORDER BY total_level DESC LIMIT ?""",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
