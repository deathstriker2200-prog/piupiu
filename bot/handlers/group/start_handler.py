from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.database.models.user import User
from bot.filters.chat_type import IsGroupChat
from bot.utils.chat_permissions import bot_is_admin

router = Router(name="group_start")
router.message.filter(IsGroupChat())


GROUP_START_TEXT = (
    "سلام رفقا تریاکی پیو پیو اومد وسط این گروه 💊🔫\n"
    "از الان همه با ۱۰۰ HP شروع می‌کنن و می‌تونن به هم بپرن\n\n"
    "برای شلیک ریپلای بزن یا منشن کن و بنویس «پیو» یا 🔫\n"
    "برای دزدی هم بنویس «دزدی @یوزرنیم»\n\n"
    "خرید سلاح، سگ، بانک و بقیه چیزا فقط تو پیوی منه، برو اونجا /start بزن 🛒"
)

NOT_ADMIN_WARNING = (
    "⚠️ یه چیزی رو جا ننداختیم\n"
    "من هنوز تو این گروه ادمین نیستم و بدون ادمین بودن نمی‌تونم درست کار کنم "
    "(مثلاً نمیتونم پیام‌های محدودشده رو بخونم یا کارای مدیریتی انجام بدم)\n\n"
    "لطفا از تنظیمات گروه من رو ادمین کن تا همه چی درست کار کنه 🙏"
)


@router.message(CommandStart())
async def cmd_group_start(message: Message, user: User) -> None:
    await message.answer(GROUP_START_TEXT)

    is_admin = await bot_is_admin(message.bot, message.chat.id)
    if not is_admin:
        await message.answer(NOT_ADMIN_WARNING)
