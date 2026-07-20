from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.database.models.user import User
from bot.database.repositories import settings_repo
from bot.filters.chat_type import IsGroupChat
from bot.utils.chat_permissions import bot_is_admin

router = Router(name="group_start")
router.message.filter(IsGroupChat())


GROUP_START_TEXT_KEY = "group_start_text"

DEFAULT_GROUP_START_TEXT = (
    "بنگ بنگ اومد وسط این گروه 💊🔫\n"
    "از الان با دستور «بنگ» میتونین به هم بپرین و پول جمع کنین\n\n"
    "برای خرید تجهیزات و لول‌آپ و... به پی‌وی ربات برید و دستور /start رو بزنید"
)

NOT_ADMIN_WARNING = (
    "⚠️ یه چیزی رو جا ننداختیم\n"
    "من هنوز تو این گروه ادمین نیستم و بدون ادمین بودن نمی‌تونم درست کار کنم "
    "(مثلاً نمیتونم پیام‌های محدودشده رو بخونم یا کارای مدیریتی انجام بدم)\n\n"
    "لطفا از تنظیمات گروه من رو ادمین کن تا همه چی درست کار کنه 🙏"
)


async def get_group_start_text() -> str:
    override = await settings_repo.get_override(GROUP_START_TEXT_KEY)
    return override or DEFAULT_GROUP_START_TEXT


@router.message(CommandStart())
async def cmd_group_start(message: Message, user: User) -> None:
    text = await get_group_start_text()
    await message.answer(text)

    is_admin = await bot_is_admin(message.bot, message.chat.id)
    if not is_admin:
        await message.answer(NOT_ADMIN_WARNING)
