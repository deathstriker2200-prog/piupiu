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
    ("dog_name", "TEXT"),
    ("attack_damage_min", "INTEGER NOT NULL DEFAULT 20"),
    ("attack_damage_max", "INTEGER NOT NULL DEFAULT 30"),
    ("attack_cooldown_until", "TEXT"),
]

USER_BUILDINGS_NEW_COLUMNS = [
    ("accumulated_income", "REAL NOT NULL DEFAULT 0"),
]

BUILDINGS_CATALOG_NEW_COLUMNS = [
    ("required_level", "INTEGER NOT NULL DEFAULT 1"),
    ("is_active", "INTEGER NOT NULL DEFAULT 1"),
    ("max_level", "INTEGER NOT NULL DEFAULT 10"),
    ("storage_cap_base", "REAL NOT NULL DEFAULT 2000"),
    ("storage_cap_growth", "REAL NOT NULL DEFAULT 1.3"),
]

DOGS_CATALOG_NEW_COLUMNS = [
    ("required_level", "INTEGER NOT NULL DEFAULT 1"),
]

EQUIPMENT_CATALOG_NEW_COLUMNS = [
    ("required_level", "INTEGER NOT NULL DEFAULT 1"),
    ("defense_percent_base", "REAL NOT NULL DEFAULT 3.0"),
    ("defense_percent_growth", "REAL NOT NULL DEFAULT 1.2"),
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
    await _add_missing_columns(conn, "user_buildings", USER_BUILDINGS_NEW_COLUMNS)
    await _add_missing_columns(conn, "dogs_catalog", DOGS_CATALOG_NEW_COLUMNS)
    await _add_missing_columns(conn, "equipment_catalog", EQUIPMENT_CATALOG_NEW_COLUMNS)
    await conn.commit()
    await _migrate_hp_to_200(conn)


async def _migrate_hp_to_200(conn: aiosqlite.Connection) -> None:
    """
    HP پایه بازی از 100 به 200 تغییر کرد
    کاربرهای قدیمی که هنوز max_hp قدیمی (بر پایه 100) دارن رو آپدیت می‌کنیم:
    - هر کاربری که max_hp کمتر از 200 داره (یعنی هنوز migration نخورده)، بر اساس لولش
      max_hp جدید (200 + (level-1)*5) رو می‌گیره
    - hp فعلیش هم به همون نسبت (درصد قبلی از max_hp قبلی) به max_hp جدید نگاشت میشه
      تا کسی که نصفه HP داشته ناگهان full/خالی نشه
    این migration فقط یک‌بار برای هر کاربر لازمه؛ چون شرط بر مبنای max_hp < 200 + رشد لوله،
      دوباره اجرا شدنش برای کاربرهای already-migrated بی‌اثره (idempotent)
    """
    HP_GAIN_PER_LEVEL = 5
    NEW_BASE_HP = 200

    cursor = await conn.execute("SELECT user_id, hp, max_hp, level FROM users")
    rows = await cursor.fetchall()

    for row in rows:
        old_max_hp = row["max_hp"]
        level = row["level"] or 1
        expected_new_max_hp = NEW_BASE_HP + (level - 1) * HP_GAIN_PER_LEVEL

        if old_max_hp is not None and old_max_hp < expected_new_max_hp:
            old_hp = row["hp"] or 0
            ratio = (old_hp / old_max_hp) if old_max_hp > 0 else 1.0
            new_hp = max(0, min(expected_new_max_hp, int(expected_new_max_hp * ratio)))
            await conn.execute(
                "UPDATE users SET hp = ?, max_hp = ? WHERE user_id = ?",
                (new_hp, expected_new_max_hp, row["user_id"]),
            )

    await conn.commit()
