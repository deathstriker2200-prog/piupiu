from typing import Optional

from bot.database.db import get_conn
from bot.database.models.dog import DogBreed, UserDog


async def list_dog_breeds() -> list[DogBreed]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM dogs_catalog ORDER BY price")
        rows = await cursor.fetchall()
        return [DogBreed.from_row(r) for r in rows]


async def get_dog_breed(dog_id: str) -> Optional[DogBreed]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM dogs_catalog WHERE dog_id = ?", (dog_id,))
        row = await cursor.fetchone()
        return DogBreed.from_row(row) if row else None


async def get_user_dogs(user_id: int) -> list[UserDog]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM user_dogs WHERE user_id = ?", (user_id,))
        rows = await cursor.fetchall()
        return [UserDog.from_row(r) for r in rows]


async def add_dog_to_user(user_id: int, dog_id: str, nickname: Optional[str] = None) -> int:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "INSERT INTO user_dogs (user_id, dog_id, nickname) VALUES (?, ?, ?)",
            (user_id, dog_id, nickname),
        )
        await conn.commit()
        return cursor.lastrowid


async def feed_dog(user_dog_id: int, xp_gain: int, fed_at_iso: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE user_dogs SET dog_xp = dog_xp + ?, last_fed_at = ? WHERE id = ?",
            (xp_gain, fed_at_iso, user_dog_id),
        )
        await conn.commit()


async def set_dog_level(user_dog_id: int, level: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE user_dogs SET dog_level = ? WHERE id = ?", (level, user_dog_id)
        )
        await conn.commit()


async def get_user_dog_by_id(user_dog_id: int) -> Optional[UserDog]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM user_dogs WHERE id = ?", (user_dog_id,))
        row = await cursor.fetchone()
        return UserDog.from_row(row) if row else None


async def get_user_dog_by_nickname(user_id: int, nickname: str) -> Optional[UserDog]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT * FROM user_dogs WHERE user_id = ? AND nickname = ? COLLATE NOCASE",
            (user_id, nickname),
        )
        row = await cursor.fetchone()
        return UserDog.from_row(row) if row else None


async def set_dog_attack_damage(user_dog_id: int, dmg_min: int, dmg_max: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE user_dogs SET attack_damage_min = ?, attack_damage_max = ? WHERE id = ?",
            (dmg_min, dmg_max, user_dog_id),
        )
        await conn.commit()


async def set_dog_attack_cooldown(user_dog_id: int, cooldown_until_iso: str) -> None:
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE user_dogs SET attack_cooldown_until = ? WHERE id = ?",
            (cooldown_until_iso, user_dog_id),
        )
        await conn.commit()


# --- غذا ---

async def list_food() -> list[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM food_catalog")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_food(food_id: str) -> Optional[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM food_catalog WHERE food_id = ?", (food_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_food_to_inventory(user_id: int, food_id: str, quantity: int) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO user_food_inventory (user_id, food_id, quantity)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, food_id) DO UPDATE SET quantity = quantity + excluded.quantity""",
            (user_id, food_id, quantity),
        )
        await conn.commit()


async def consume_food(user_id: int, food_id: str) -> bool:
    """یک واحد غذا مصرف می‌کنه، اگه موجودی کافی نبود False برمی‌گردونه"""
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT quantity FROM user_food_inventory WHERE user_id = ? AND food_id = ?",
            (user_id, food_id),
        )
        row = await cursor.fetchone()
        if row is None or row["quantity"] <= 0:
            return False
        await conn.execute(
            "UPDATE user_food_inventory SET quantity = quantity - 1 WHERE user_id = ? AND food_id = ?",
            (user_id, food_id),
        )
        await conn.commit()
        return True
