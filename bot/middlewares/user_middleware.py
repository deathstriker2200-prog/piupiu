from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.database.repositories import user_repo
from bot.texts.common_texts import banned_message


class UserRegistrationMiddleware(BaseMiddleware):
    """
    قبل از هر هندلر:
    ۱- کاربر رو داخل دیتابیس می‌سازه اگه وجود نداشت
    ۲- اگه بن بود جلوی ادامه پردازش رو می‌گیره
    ۳- شی user رو داخل data تزریق می‌کنه تا هندلرها لازم نباشه دوباره query بزنن
    ۴- اگه پیام تو یه گروه اومده، آخرین گروه فعال کاربر رو ثبت می‌کنه
       (این جایگزین یه GROUP_ID ثابت میشه - ربات باید تو هر گروهی که بهش اضافه بشه کار کنه)
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = None
        chat_id = None
        chat_type = None

        if isinstance(event, Message) and event.from_user:
            tg_user = event.from_user
            chat_id = event.chat.id
            chat_type = event.chat.type
        elif isinstance(event, CallbackQuery) and event.from_user:
            tg_user = event.from_user
            if event.message:
                chat_id = event.message.chat.id
                chat_type = event.message.chat.type

        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        user = await user_repo.get_or_create_user(
            tg_user.id, tg_user.username, tg_user.full_name
        )

        if user.is_banned:
            if isinstance(event, Message):
                await event.answer(banned_message())
            elif isinstance(event, CallbackQuery):
                await event.answer(banned_message(), show_alert=True)
            return None

        if chat_id is not None and chat_type in ("group", "supergroup"):
            if user.last_active_group_id != chat_id:
                await user_repo.set_last_active_group(tg_user.id, chat_id)
                user.last_active_group_id = chat_id

        data["user"] = user
        return await handler(event, data)
