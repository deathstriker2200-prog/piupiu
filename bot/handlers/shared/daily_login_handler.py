from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.models.user import User
from bot.services.daily_login_service import DailyLoginError, claim_daily
from bot.utils.formatting import format_currency

router = Router(name="daily_login_commands")


@router.message(Command("روزانه"))
async def cmd_daily_login(message: Message, user: User) -> None:
    try:
        result = await claim_daily(user.user_id)
    except DailyLoginError as e:
        if str(e) == "already_claimed_today":
            await message.answer("امروز رو قبلا گرفتی فردا دوباره بیا 📅")
        else:
            await message.answer("یه مشکلی پیش اومد دوباره امتحان کن")
        return

    lines = [
        f"📅 حضور روزانه ثبت شد روز {result['streak']} پشت سر هم 🔥",
        f"گرفتی: {format_currency(result['reward_tiriak'])} تریاک‌پوینت و {result['reward_xp']} XP",
    ]
    if result["reward_diamond"] > 0:
        lines.append(f"💎 {result['reward_diamond']} الماس هم جایزه گرفتی")
    if result["used_freeze"]:
        lines.append("🧊 یه روز رو جا انداخته بودی ولی آیتم Freeze نجاتت داد")

    await message.answer("\n".join(lines))
