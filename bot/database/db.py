import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aiosqlite

_db_path: str = "data/tiryaki.db"


async def init_db(db_path: str) -> None:
    """دیتابیس رو می‌سازه (اگه نبود)، اسکیمای پایه + نسخه ۲ رو اجرا می‌کنه و migration های ستونی رو اعمال می‌کنه"""
    global _db_path
    _db_path = db_path
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    base_schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    v2_schema_path = os.path.join(os.path.dirname(__file__), "schema_v2.sql")

    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("PRAGMA foreign_keys = ON;")

        with open(base_schema_path, "r", encoding="utf-8") as f:
            await conn.executescript(f.read())
        await conn.commit()

        if os.path.exists(v2_schema_path):
            with open(v2_schema_path, "r", encoding="utf-8") as f:
                await conn.executescript(f.read())
            await conn.commit()

        from bot.database.migrations import apply_column_migrations
        await apply_column_migrations(conn)

    from bot.database.seed_data import seed_all
    await seed_all()

    from bot.database.seed_data_v2 import seed_all_v2
    await seed_all_v2()


@asynccontextmanager
async def get_conn() -> AsyncIterator[aiosqlite.Connection]:
    """یک اتصال جدید به دیتابیس میده - برای هر عملیات یک اتصال کوچک باز میشه"""
    conn = await aiosqlite.connect(_db_path)
    conn.row_factory = aiosqlite.Row
    try:
        await conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
    finally:
        await conn.close()
