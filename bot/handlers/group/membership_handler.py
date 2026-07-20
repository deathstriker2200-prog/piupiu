from aiogram import Bot, Router
from aiogram.types import ChatMemberUpdated

from bot.handlers.group.start_handler import NOT_ADMIN_WARNING, get_group_start_text

router = Router(name="group_membership")


@router.my_chat_member()
async def on_bot_membership_changed(event: ChatMemberUpdated, bot: Bot) -> None:
    """
    وقتی ربات به یه گروه اضافه میشه یا وضعیت عضویتش تغییر می‌کنه این صدا زده میشه
    اگه تازه اضافه شده: خوش‌آمد + چک ادمین بودن
    اگه از حالت عادی به ادمین ارتقا پیدا کرد: پیام تایید بده
    """
    if event.chat.type not in ("group", "supergroup"):
        return

    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status

    # ربات تازه به گروه اضافه شده (از left/kicked به member/administrator)
    if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
        text = await get_group_start_text()
        await bot.send_message(event.chat.id, text)
        if new_status != "administrator":
            await bot.send_message(event.chat.id, NOT_ADMIN_WARNING)
        return

    # ربات از member به administrator ارتقا پیدا کرد
    if old_status == "member" and new_status == "administrator":
        await bot.send_message(
            event.chat.id, "✅ عالی شد الان ادمینم همه چی درست کار می‌کنه بزنید بریم 🔥"
        )

    # ربات از ادمین به عضو عادی تنزل پیدا کرد
    if old_status == "administrator" and new_status == "member":
        await bot.send_message(event.chat.id, NOT_ADMIN_WARNING)
