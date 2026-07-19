from typing import Optional

from bot.database.db import get_conn


async def get_bank(user_id: int) -> Optional[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT * FROM bank_accounts WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def deposit(user_id: int, amount: int) -> bool:
    """برمی‌گردونه True اگه واریز موفق بود (ظرفیت کافی بود)"""
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT balance, capacity FROM bank_accounts WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return False
        if row["balance"] + amount > row["capacity"]:
            return False
        await conn.execute(
            "UPDATE bank_accounts SET balance = balance + ?, updated_at = datetime('now') WHERE user_id = ?",
            (amount, user_id),
        )
        await conn.execute(
            "UPDATE users SET tiriak_point = tiriak_point - ? WHERE user_id = ?",
            (amount, user_id),
        )
        await conn.commit()
        return True


async def withdraw(user_id: int, amount: int) -> bool:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT balance FROM bank_accounts WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None or row["balance"] < amount:
            return False
        await conn.execute(
            "UPDATE bank_accounts SET balance = balance - ?, updated_at = datetime('now') WHERE user_id = ?",
            (amount, user_id),
        )
        await conn.execute(
            "UPDATE users SET tiriak_point = tiriak_point + ? WHERE user_id = ?",
            (amount, user_id),
        )
        await conn.commit()
        return True


async def upgrade_capacity(user_id: int, new_capacity: int, new_level: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE bank_accounts SET capacity = ?, level = ? WHERE user_id = ?",
            (new_capacity, new_level, user_id),
        )
        await conn.commit()
