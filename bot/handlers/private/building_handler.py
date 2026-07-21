from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import building_repo
from bot.services.building_service import (
    BuildingError,
    building_level_cap_for_player_level,
    collect_income,
    get_building_progress,
    income_per_hour_for_level,
    storage_cap_for_level,
    upgrade_building,
    upgrade_cost,
)
from bot.texts.common_texts import not_enough_level, not_enough_money
from bot.utils.formatting import format_currency

router = Router(name="private_building")

PROGRESS_BAR_SEGMENTS = 10


def _progress_bar(current: float, cap: float) -> str:
    if cap <= 0:
        return "▱" * PROGRESS_BAR_SEGMENTS
    filled = min(PROGRESS_BAR_SEGMENTS, int((current / cap) * PROGRESS_BAR_SEGMENTS))
    return "▰" * filled + "▱" * (PROGRESS_BAR_SEGMENTS - filled)


def _lock_mark(user_level: int, required_level: int, level_cap_ok: bool, can_afford: bool) -> str:
    if user_level < required_level:
        return "🔒"
    if not level_cap_ok:
        return "⏫"
    if not can_afford:
        return "🔴"
    return "🟢"


@router.callback_query(lambda c: c.data == "menu:buildings")
async def cb_buildings_menu(callback: CallbackQuery, user: User) -> None:
    catalog = await building_repo.list_building_types()
    owned = await building_repo.get_user_buildings(user.user_id)
    levels = {b["building_id"]: b["level"] for b in owned}

    sorted_catalog = sorted(catalog, key=lambda b: b.required_level)

    rows = []
    for b in sorted_catalog:
        level = levels.get(b.building_id, 0)
        cost = upgrade_cost(level)
        level_cap = building_level_cap_for_player_level(user.level)
        level_cap_ok = level < level_cap
        mark = _lock_mark(user.level, b.required_level, level_cap_ok, user.tiriak_point >= cost)
        action_label = "ساخت" if level == 0 else f"ارتقا به لول {level + 1}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{mark} {b.emoji} {b.name_fa} (لول {level}/{b.max_level}) — {action_label}",
                    callback_data=f"building_detail:{b.building_id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    await callback.message.edit_text(
        "🏗 ساختمان‌های تو\n\n"
        "🟢 قابل ساخت/ارتقا   🔴 پول کافی نداری   🔒 لول لازم رو نداری   ⏫ باید اول لول بازیکنیت بره بالاتر",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("building_detail:"))
async def cb_building_detail(callback: CallbackQuery, user: User) -> None:
    building_id = callback.data.split(":", 1)[1]
    building_type = await building_repo.get_building_type(building_id)
    if building_type is None:
        await callback.answer("ساختمان پیدا نشد", show_alert=True)
        return

    progress = await get_building_progress(user.user_id, building_id)
    level = progress["level"]
    cost = upgrade_cost(level)
    level_cap = building_level_cap_for_player_level(user.level)

    locked_by_level = user.level < building_type.required_level
    locked_by_cap = level >= level_cap and level < building_type.max_level
    maxed = level >= building_type.max_level

    action_label = "ساخت" if level == 0 else "ارتقاء"
    required_for_action = building_type.required_level if level == 0 else (level * 5)

    next_level = level + 1 if level < building_type.max_level else level
    next_income = income_per_hour_for_level(building_type, next_level)

    text = (
        f"{building_type.emoji} {building_type.name_fa}\n\n"
        f"لول فعلی: {level}\n"
        f"لول لازم برای {action_label}: {required_for_action}\n"
    )

    if level == 0:
        text += f"هزینه ساخت اولیه: {format_currency(cost)}TP\n"
    elif not maxed:
        text += (
            f"هزینه ارتقاء به لول {next_level}: {format_currency(cost)}TP\n"
            f"درآمد ساعتی بعد از ارتقاء: {format_currency(int(next_income))}TP در ساعت "
            f"(الان: {format_currency(int(progress['per_hour']))}TP در ساعت)\n"
        )
    else:
        text += "🏆 این ساختمان به حداکثر لول رسیده\n"

    if level > 0:
        bar = _progress_bar(progress["accumulated"], progress["cap"])
        text += (
            f"\nمقدار درآمد بدست‌آمده:\n"
            f"{bar} {format_currency(progress['accumulated'])}/{format_currency(int(progress['cap']))}TP\n"
            f"درآمد ساعتی فعلی: {format_currency(int(progress['per_hour']))}TP در ساعت"
        )

    if locked_by_level:
        text += f"\n\n🔒 لولت کافی نیست (لول تو: {user.level}, لازم: {building_type.required_level})"
    elif locked_by_cap:
        text += f"\n\n⏫ برای ارتقای بعدی باید لول بازیکنیت به {required_for_action} برسه (الان: {user.level})"

    rows = []
    if not locked_by_level and not locked_by_cap and not maxed:
        button_label = "✅ ساخت" if level == 0 else "✅ ارتقاء"
        rows.append(
            [InlineKeyboardButton(text=button_label, callback_data=f"building_upgrade:{building_id}")]
        )
    if level > 0 and progress["accumulated"] > 0:
        rows.append(
            [InlineKeyboardButton(text="💰 برداشت درآمد", callback_data=f"building_collect:{building_id}")]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:buildings")])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("building_upgrade:"))
async def cb_building_upgrade(callback: CallbackQuery, user: User) -> None:
    building_id = callback.data.split(":", 1)[1]
    try:
        new_level = await upgrade_building(user.user_id, building_id)
    except BuildingError as e:
        error = str(e)
        if error.startswith("level_required:"):
            required = int(error.split(":", 1)[1])
            await callback.answer(not_enough_level(required), show_alert=True)
        elif error.startswith("player_level_cap:"):
            required = int(error.split(":", 1)[1])
            await callback.answer(f"⏫ باید اول لول بازیکنیت به {required} برسه", show_alert=True)
        elif error == "max_level_reached":
            await callback.answer("🏆 این ساختمان از قبل به حداکثر لول رسیده", show_alert=True)
        else:
            await callback.answer(not_enough_money(), show_alert=True)
        return
    await callback.answer(f"✅ ساختمان رفت لول {new_level}", show_alert=True)
    await cb_building_detail(callback, user)


@router.callback_query(lambda c: c.data and c.data.startswith("building_collect:"))
async def cb_building_collect(callback: CallbackQuery, user: User) -> None:
    building_id = callback.data.split(":", 1)[1]
    try:
        income = await collect_income(user.user_id, building_id)
    except BuildingError:
        await callback.answer("چیزی برای برداشت نیست", show_alert=True)
        return
    await callback.answer(f"💰 {format_currency(income)} تریاک‌پوینت گرفتی", show_alert=True)
    await cb_building_detail(callback, user)
