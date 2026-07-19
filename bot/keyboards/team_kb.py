from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.common import accept_reject_keyboard


def join_request_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """برای لیدر تیم - قبول ✅ سبز یا رد ❌ قرمز درخواست عضویت"""
    return accept_reject_keyboard(
        accept_callback=f"team_req_accept:{request_id}",
        reject_callback=f"team_req_reject:{request_id}",
    )


def team_menu_keyboard(has_team: bool) -> InlineKeyboardMarkup:
    if has_team:
        rows = [
            [InlineKeyboardButton(text="📋 اعضا", callback_data="team:members")],
            [InlineKeyboardButton(text="⬆️ ارتقای تیم", callback_data="team:upgrades")],
            [InlineKeyboardButton(text="🚪 خروج از تیم", callback_data="team:leave_confirm")],
        ]
    else:
        rows = [
            [InlineKeyboardButton(text="🆕 ساخت تیم", callback_data="team:create")],
            [InlineKeyboardButton(text="🔍 جستجوی تیم", callback_data="team:search")],
        ]
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
