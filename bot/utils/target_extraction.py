from typing import Optional

from aiogram.types import Message


async def extract_target_user_id(message: Message) -> Optional[int]:
    """
    هدف حمله/دزدی رو از پیام استخراج می‌کنه
    یا از طریق ریپلای روی پیام طرف یا از طریق منشن @username
    """
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id

    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention" and entity.user:
                return entity.user.id
            if entity.type == "mention":
                # mention ساده فقط username میده، باید جدا resolve بشه
                # این مورد نیاز به دسترسی به دیتابیس یوزرها داره (بر اساس username ذخیره شده)
                username = message.text[entity.offset + 1 : entity.offset + entity.length]
                from bot.database.db import get_conn

                async with get_conn() as conn:
                    cursor = await conn.execute(
                        "SELECT user_id FROM users WHERE username = ?", (username,)
                    )
                    row = await cursor.fetchone()
                    if row:
                        return row["user_id"]
    return None
