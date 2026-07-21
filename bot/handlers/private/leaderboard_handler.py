from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import team_repo, user_repo
from bot.keyboards.common import back_keyboard
from bot.utils.formatting import format_currency

router = Router(name="private_leaderboard")

BOARD_LABELS = {
    "level": "🌟 بیشترین لول",
    "xp": "✨ بیشترین ایکس‌پی",
    "tiriak_point": "💊 بیشترین تریاک‌پوینت",
    "kills": "💀 بیشترین کشته",
}


def leaderboard_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"lb:{key}")]
        for key, label in BOARD_LABELS.items()
    ]
    rows.append([InlineKeyboardButton(text="🏴 بهترین تیم", callback_data="lb:team")])
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(lambda c: c.data == "menu:leaderboard")
async def cb_leaderboard_menu(callback: CallbackQuery, user: User) -> None:
    await callback.message.edit_text("🏆 لیدربرد کدومو ببینم؟", reply_markup=leaderboard_menu_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("lb:") and c.data != "lb:team")
async def cb_leaderboard_show(callback: CallbackQuery, user: User) -> None:
    key = callback.data.split(":", 1)[1]
    top_users = await user_repo.get_leaderboard(key, limit=10)

    lines = [BOARD_LABELS.get(key, key), ""]
    for i, u in enumerate(top_users, start=1):
        name = u.full_name or u.username or "بازیکن"
        value = getattr(u, key)
        if key == "tiriak_point":
            value = format_currency(value)
        lines.append(f"{i}. {name} — {value}")

    await callback.message.edit_text("\n".join(lines), reply_markup=back_keyboard("menu:leaderboard"))
    await callback.answer()


@router.callback_query(lambda c: c.data == "lb:team")
async def cb_leaderboard_team(callback: CallbackQuery, user: User) -> None:
    teams = await team_repo.get_leaderboard_teams(limit=10)
    lines = ["🏴 بهترین تیم‌ها", ""]
    for i, t in enumerate(teams, start=1):
        lines.append(f"{i}. {t['logo_emoji'] or ''} {t['name']} — مجموع لول {t['total_level']}")
    await callback.message.edit_text("\n".join(lines), reply_markup=back_keyboard("menu:leaderboard"))
    await callback.answer()
