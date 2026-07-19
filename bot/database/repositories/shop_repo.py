from typing import Optional

from bot.database.db import get_conn


async def list_shop_items(category: Optional[str] = None) -> list[dict]:
    async with get_conn() as conn:
        if category:
            cursor = await conn.execute(
                "SELECT * FROM shop_items WHERE is_active = 1 AND category = ?", (category,)
            )
        else:
            cursor = await conn.execute("SELECT * FROM shop_items WHERE is_active = 1")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_shop_item(item_id: str) -> Optional[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute("SELECT * FROM shop_items WHERE item_id = ?", (item_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def create_shop_item(
    item_id: str,
    name_fa: str,
    emoji: Optional[str],
    category: str,
    price: int,
    price_currency: str,
    effect_json: Optional[str] = None,
) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO shop_items (item_id, name_fa, emoji, category, price, price_currency, effect_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (item_id, name_fa, emoji, category, price, price_currency, effect_json),
        )
        await conn.commit()


async def remove_shop_item(item_id: str) -> None:
    async with get_conn() as conn:
        await conn.execute("UPDATE shop_items SET is_active = 0 WHERE item_id = ?", (item_id,))
        await conn.commit()


async def give_item_to_user(user_id: int, item_id: str, quantity: int = 1) -> None:
    async with get_conn() as conn:
        await conn.execute(
            """INSERT INTO user_items (user_id, item_id, quantity) VALUES (?, ?, ?)
               ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + excluded.quantity""",
            (user_id, item_id, quantity),
        )
        await conn.commit()


async def get_user_items(user_id: int) -> list[dict]:
    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT ui.*, si.name_fa, si.emoji FROM user_items ui
               JOIN shop_items si ON ui.item_id = si.item_id
               WHERE ui.user_id = ? AND ui.quantity > 0""",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
