"""
تنظیم منوی دستورات تلگرام (همون لیستی که با زدن / تو تلگرام باز میشه)
دستورات عمومی برای همه نمایش داده میشن
دستورات ادمین فقط تو چت خصوصی خود ادمین‌ها (BotCommandScopeChat) اضافه میشن
تا بقیه کاربرها اصلا تو اتوکامپلیت‌شون نبینن

نکته: تلگرام فقط حروف انگلیسی کوچیک، عدد و آندرلاین رو تو اسم کامند قبول می‌کنه
پس همه دستورات باید انگلیسی باشن (توضیحشون می‌تونه فارسی بمونه)
"""

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from bot.config.settings import settings

DEFAULT_COMMANDS = [
    BotCommand(command="start", description="شروع / منوی اصلی"),
    BotCommand(command="help", description="راهنمای کامل دستورات"),
    BotCommand(command="profile", description="نمایش پروفایل کامل"),
    BotCommand(command="achievements", description="لیست دستاوردهای تو"),
    BotCommand(command="badges", description="نشان‌هایی که گرفتی"),
    BotCommand(command="daily", description="گرفتن جایزه حضور روزانه"),
    BotCommand(command="menu", description="بازکردن دوباره منوی اصلی (پیوی)"),
]

ADMIN_EXTRA_COMMANDS = [
    BotCommand(command="admin", description="پنل مدیریت ربات"),
    BotCommand(command="backup", description="گرفتن فایل بک‌آپ دیتابیس"),
    BotCommand(command="restore", description="جایگزینی دیتابیس با فایل بک‌آپ"),
    BotCommand(command="setgroupwelcome", description="تغییر متن خوشامد گروه"),
    BotCommand(command="setdmwelcome", description="تغییر متن خوشامد پیوی"),
]


async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(DEFAULT_COMMANDS, scope=BotCommandScopeDefault())

    for admin_id in settings.admin_ids:
        try:
            await bot.set_my_commands(
                DEFAULT_COMMANDS + ADMIN_EXTRA_COMMANDS,
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except Exception:
            # اگه ادمین هنوز پیوی رو استارت نکرده باشه ست کردن کامند برای چتش fail میشه، مهم نیست
            pass
