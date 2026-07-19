from aiogram import Router
from aiogram.types import CallbackQuery

from bot.database.models.user import User
from bot.database.repositories import quest_repo
from bot.keyboards.common import back_keyboard
from bot.services.quest_service import period_start

router = Router(name="private_quest")

PERIOD_LABELS = {"daily": "روزانه", "weekly": "هفتگی", "monthly": "ماهانه"}


@router.callback_query(lambda c: c.data == "menu:quests")
async def cb_quests_menu(callback: CallbackQuery, user: User) -> None:
    quests = await quest_repo.list_active_quests()
    if not quests:
        await callback.message.edit_text(
            "الان کوئستی فعال نیست بعدا سر بزن", reply_markup=back_keyboard("menu:main")
        )
        await callback.answer()
        return

    lines = ["📜 کوئست‌های فعال\n"]
    for q in quests:
        period_start_val = period_start(q.period)
        progress = await quest_repo.get_progress(user.user_id, q.quest_id, period_start_val)
        current = progress["progress"] if progress else 0
        done = "✅" if (progress and progress["is_completed"]) else ""
        lines.append(
            f"{PERIOD_LABELS.get(q.period, q.period)} | {q.title} {done}\n"
            f"پیشرفت: {min(current, q.goal_amount)}/{q.goal_amount}"
        )

    await callback.message.edit_text("\n\n".join(lines), reply_markup=back_keyboard("menu:main"))
    await callback.answer()
