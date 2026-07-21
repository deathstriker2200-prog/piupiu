from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import settings
from bot.database.models.user import User

router = Router(name="help_commands")


MEMBER_COMMANDS_TEXT = (
    "📖 راهنمای دستورات بنگ بنگ\n\n"
    "🔫 تو گروه:\n"
    "«بنگ» یا 🔫 (با ریپلای یا منشن) — شلیک به یه بازیکن\n"
    "/steal (با ریپلای یا منشن) — تلاش برای دزدی\n"
    "/start — شروع تو گروه\n\n"
    "💬 همه‌جا (گروه و پیوی):\n"
    "/achievements — لیست دستاوردهات\n"
    "/badges — نشان‌هایی که گرفتی\n"
    "/daily — گرفتن جایزه حضور روزانه\n\n"
    "🛒 تو پیوی ربات:\n"
    "/start — منوی اصلی (فروشگاه، بانک، ساختمان، تیم و غیره)\n"
    "/profile — پروفایل کامل با آمار و عکس\n"
    "/menu — بازکردن دوباره منوی اصلی"
)


ADMIN_COMMANDS_TEXT = (
    "\n\n⚙️ دستورات ادمین:\n"
    "/admin — باز کردن پنل ادمین (آمار، بن/آن‌بن، دادن پول/ایکس‌پی/الماس، ارسال همگانی و غیره)\n"
    "/backup — گرفتن فایل بک‌آپ از دیتابیس فعلی\n"
    "/restore — جایگزین کردن دیتابیس با یه فایل بک‌آپ\n"
    "/setgroupwelcome — تغییر متن خوشامدگویی گروه\n"
    "/setdmwelcome — تغییر متن خوشامدگویی پیوی"
)


@router.message(Command("help"))
async def cmd_help(message: Message, user: User) -> None:
    text = MEMBER_COMMANDS_TEXT
    if message.from_user and message.from_user.id in settings.admin_ids:
        text += ADMIN_COMMANDS_TEXT
    await message.answer(text)
