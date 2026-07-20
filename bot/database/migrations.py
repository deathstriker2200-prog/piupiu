"""
Migration های پایتونی برای ستون‌های جدید
ALTER TABLE ADD COLUMN با اجرای دوباره خطا میده پس اول چک می‌کنیم ستون هست یا نه
این تابع idempotent هست و هر بار استارت ربات صدا زده میشه
"""

import aiosqlite

USERS_NEW_COLUMNS = [
    ("energy", "INTEGER NOT NULL DEFAULT 100"),
    ("max_energy", "INTEGER NOT NULL DEFAULT 100"),
    ("energy_updated_at", "TEXT"),
    ("luck", "INTEGER NOT NULL DEFAULT 10"),
    ("combo_count", "INTEGER NOT NULL DEFAULT 0"),
    ("combo_updated_at", "TEXT"),
    ("reputation", "INTEGER NOT NULL DEFAULT 0"),
    ("login_streak", "INTEGER NOT NULL DEFAULT 0"),
    ("last_login_at", "TEXT"),
    ("streak_freeze_available", "INTEGER NOT NULL DEFAULT 0"),
    ("last_active_group_id", "INTEGER"),
]

USER_DOGS_NEW_COLUMNS = [
    ("mood", "INTEGER NOT NULL DEFAULT 80"),
    ("hunger", "INTEGER NOT NULL DEFAULT 80"),
    ("sleep_level", "INTEGER NOT NULL DEFAULT 100"),
    ("loyalty", "INTEGER NOT NULL DEFAULT 50"),
    ("last_stats_update_at", "TEXT"),
    ("is_weakened", "INTEGER NOT NULL DEFAULT 0"),
]

BUILDINGS_CATALOG_NEW_COLUMNS = [
    ("required_level", "INTEGER NOT NULL DEFAULT 1"),
]

DOGS_CATALOG_NEW_COLUMNS = [
    ("required_level", "INTEGER NOT NULL DEFAULT 1"),
]

EQUIPMENT_CATALOG_NEW_COLUMNS = [
    ("required_level", "INTEGER NOT NULL DEFAULT 1"),
]


async def _existing_columns(conn: aiosqlite.Connection, table: str) -> set[str]:
    cursor = await conn.execute(f"PRAGMA table_info({table})")
    rows = await cursor.fetchall()
    return {row[1] for row in rows}


async def _add_missing_columns(
    conn: aiosqlite.Connection, table: str, columns: list[tuple[str, str]]
) -> None:
    existing = await _existing_columns(conn, table)
    for col_name, col_def in columns:
        if col_name not in existing:
            await conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")


async def apply_column_migrations(conn: aiosqlite.Connection) -> None:
    await _add_missing_columns(conn, "users", USERS_NEW_COLUMNS)
    await _add_missing_columns(conn, "user_dogs", USER_DOGS_NEW_COLUMNS)
    await _add_missing_columns(conn, "buildings_catalog", BUILDINGS_CATALOG_NEW_COLUMNS)
    await _add_missing_columns(conn, "dogs_catalog", DOGS_CATALOG_NEW_COLUMNS)
    await _add_missing_columns(conn, "equipment_catalog", EQUIPMENT_CATALOG_NEW_COLUMNS)
    await conn.commit()
