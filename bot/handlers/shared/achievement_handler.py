from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.models.user import User
from bot.services.achievement_service import get_achievement_summary, get_user_achievements
from bot.services.badge_service import get_user_badges

router = Router(name="achievement_commands")

TIER_LABELS = {"bronze": "🥉", "silver": "🥈", "gold": "🥇", "platinum": "💎"}


@router.message(Command("achievements"))
async def cmd_achievements(message: Message, user: User) -> None:
    all_ach = await get_user_achievements(user.user_id)
    summary = await get_achievement_summary(user.user_id)

    unlocked = [a for a in all_ach if a["unlocked_at"]]
    in_progress = [a for a in all_ach if not a["unlocked_at"] and a["progress"] > 0]

    lines = [f"🏅 دستاوردهای تو ({summary['unlocked']}/{summary['total']})\n"]

    if unlocked:
        lines.append("✅ گرفته‌شده:")
        for a in unlocked[:15]:
            tier_icon = TIER_LABELS.get(a["tier"], "")
            lines.append(f"{a['icon']} {a['title']} {tier_icon}")
        if len(unlocked) > 15:
            lines.append(f"... و {len(unlocked) - 15} تای دیگه")
        lines.append("")

    if in_progress:
        lines.append("🔄 در حال پیشرفت:")
        for a in in_progress[:10]:
            lines.append(f"{a['icon']} {a['title']} — {a['progress']}/{a['goal_amount']}")

    if not unlocked and not in_progress:
        lines.append("هنوز هیچ دستاوردی نگرفتی، برو بازی کن تا شروع بشه 🎮")

    await message.answer("\n".join(lines))


@router.message(Command("badges"))
async def cmd_badges(message: Message, user: User) -> None:
    badges = await get_user_badges(user.user_id)

    if not badges:
        await message.answer(
            "هنوز هیچ نشانی نگرفتی 🏷\n"
            "با فعالیت تو بازی (جنگیدن، پول درآوردن، نگهداری سگ و غیره) نشان می‌گیری"
        )
        return

    lines = [f"🏷 نشان‌های تو ({len(badges)})\n"]
    for b in badges:
        pin_mark = "📌 " if b["is_pinned"] else ""
        lines.append(f"{pin_mark}{b['icon']} {b['title']}\n   {b['description']}")

    await message.answer("\n\n".join(lines))
