"""
دستورات مستقیم گروه: /shop, /profile, /leaderboard
این‌ها دقیقا همون بخش‌هایی هستن که تو منوی پیوی هم هستن، ولی مستقیم تو خود گروه با دستور اسلش باز میشن
بدون دکمه «بازگشت» چون تو گروه چیزی برای برگشتن بهش نیست
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.models.user import User
from bot.database.repositories import user_repo
from bot.filters.chat_type import IsGroupChat
from bot.handlers.private.profile_handler import _build_profile_text
from bot.handlers.private.shop_handler import build_weapon_shop_text
from bot.keyboards.shop_kb import weapon_shop_keyboard
from bot.utils.formatting import format_currency

router = Router(name="group_direct_commands")
router.message.filter(IsGroupChat())


@router.message(Command("shop"))
async def group_cmd_shop(message: Message, user: User) -> None:
    text = await build_weapon_shop_text(user)
    await message.answer(text, reply_markup=weapon_shop_keyboard(include_back_button=False))


@router.message(Command("profile"))
async def group_cmd_profile(message: Message, user: User) -> None:
    text = await _build_profile_text(user)
    await message.answer(text)


BOARD_LABELS = {
    "level": "🌟 بیشترین لول",
    "xp": "✨ بیشترین ایکس‌پی",
    "tiriak_point": "💊 بیشترین تریاک‌پوینت",
    "kills": "💀 بیشترین کشته",
}


@router.message(Command("leaderboard"))
async def group_cmd_leaderboard(message: Message, user: User) -> None:
    top_users = await user_repo.get_leaderboard("level", limit=10)
    lines = ["🏆 لیدربرد (بر اساس لول)", ""]
    for i, u in enumerate(top_users, start=1):
        name = u.full_name or u.username or "بازیکن"
        lines.append(f"{i}. {name} — لول {u.level} | {format_currency(u.tiriak_point)} تریاک‌پوینت")
    if not top_users:
        lines.append("هنوز کسی تو لیدربرد نیست")
    await message.answer("\n".join(lines))
