from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import building_repo
from bot.services.building_service import BUILDING_UPGRADE_BASE_COST, BuildingError, collect_income, upgrade_building
from bot.texts.common_texts import not_enough_level, not_enough_money
from bot.utils.formatting import format_currency

router = Router(name="private_building")


def _lock_mark(user_level: int, required_level: int, can_afford: bool) -> str:
    if user_level < required_level:
        return "❌"
    if not can_afford:
        return "🔒"
    return "✅"


@router.callback_query(lambda c: c.data == "menu:buildings" or c.data == "shop_cat:buildings")
async def cb_buildings_menu(callback: CallbackQuery, user: User) -> None:
    catalog = await building_repo.list_building_types()
    owned = await building_repo.get_user_buildings(user.user_id)
    levels = {b["building_id"]: b["level"] for b in owned}

    # مرتب‌سازی: اول بر اساس لول لازم (ارزون/ساده‌تر اول)، بعد قیمت ساخت فعلی
    sorted_catalog = sorted(catalog, key=lambda b: (b.required_level, b.base_value))

    rows = []
    for b in sorted_catalog:
        level = levels.get(b.building_id, 0)
        cost = BUILDING_UPGRADE_BASE_COST * (level + 1)
        mark = _lock_mark(user.level, b.required_level, user.tiriak_point >= cost)
        action_label = "ساخت" if level == 0 else f"ارتقا به {level + 1}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"{mark} {b.emoji} {b.name_fa} (لول فعلی {level}, نیاز لول {b.required_level}) — "
                        f"{action_label}: {format_currency(cost)}💊"
                    ),
                    callback_data=f"building_detail:{b.building_id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    await callback.message.edit_text(
        "🏗 ساختمان‌ها - قیمت ساخت/ارتقای بعدی و لول لازم کنار هرکدوم نوشته شده",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("building_detail:"))
async def cb_building_detail(callback: CallbackQuery, user: User) -> None:
    building_id = callback.data.split(":", 1)[1]
    building_type = await building_repo.get_building_type(building_id)
    owned = await building_repo.get_user_building(user.user_id, building_id)
    level = owned["level"] if owned else 0
    cost = BUILDING_UPGRADE_BASE_COST * (level + 1)

    locked = user.level < building_type.required_level
    action_label = "ساخت اولیه" if level == 0 else f"ارتقا به لول {level + 1}"

    text = (
        f"{building_type.emoji} {building_type.name_fa}\n\n"
        f"لول فعلی: {level}\n"
        f"لول لازم برای {'ساخت' if level == 0 else 'ارتقا'}: {building_type.required_level}\n"
        f"هزینه {action_label}: {format_currency(cost)}💊"
    )
    if locked:
        text += f"\n\n❌ لولت کافی نیست (لول تو: {user.level})"

    button_label = "🛠 ساخت" if level == 0 else "⬆️ ارتقا"
    rows = []
    if not locked:
        rows.append(
            [InlineKeyboardButton(text=button_label, callback_data=f"building_upgrade:{building_id}")]
        )
    if building_type.effect_type in ("income", "fixed_income") and level > 0:
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
