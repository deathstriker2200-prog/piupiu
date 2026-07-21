from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import equipment_repo, user_repo
from bot.texts.common_texts import not_enough_level, not_enough_money
from bot.utils.formatting import format_currency

router = Router(name="private_equipment")

EQUIPMENT_UPGRADE_BASE_COST = 800
EQUIPMENT_UPGRADE_GROWTH = 1.5
EQUIPMENT_MAX_LEVEL = 8

SLOT_LABELS_FA = {
    "vest": "تنه (جلیقه)",
    "helmet": "سر (کلاه)",
    "boots": "پا (چکمه)",
    "gloves": "دست (دستکش)",
}


def _cost_for_level(current_level: int) -> int:
    return int(EQUIPMENT_UPGRADE_BASE_COST * (EQUIPMENT_UPGRADE_GROWTH ** current_level))


def _defense_percent(base: float, growth: float, level: int) -> float:
    if level <= 0:
        return 0.0
    return base * (growth ** (level - 1))


@router.callback_query(lambda c: c.data == "menu:equipment" or c.data == "shop_cat:equipment")
async def cb_equipment_menu(callback: CallbackQuery, user: User) -> None:
    catalog = await equipment_repo.list_equipment_catalog()
    owned = await equipment_repo.get_user_equipment(user.user_id)
    levels = {e["equipment_id"]: e["level"] for e in owned}
    total_defense = await equipment_repo.get_total_defense_percent(user.user_id)

    rows = []
    for item in catalog:
        level = levels.get(item["equipment_id"], 0)
        cost = _cost_for_level(level)
        required_level = item.get("required_level", 1)
        maxed = level >= EQUIPMENT_MAX_LEVEL

        if level == 0 and user.level < required_level:
            mark = "🔒"
        elif maxed:
            mark = "🏆"
        elif user.tiriak_point < cost:
            mark = "🔴"
        else:
            mark = "🟢"

        action_label = "ساخت" if level == 0 else f"ارتقا به لول {level + 1}"
        slot_label = SLOT_LABELS_FA.get(item["slot"], item["slot"])
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{mark} {item['emoji']} {item['name_fa']} ({slot_label}) — لول {level}/{EQUIPMENT_MAX_LEVEL}",
                    callback_data=f"equip_detail:{item['equipment_id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    await callback.message.edit_text(
        "🦺 تجهیزات دفاعی\n\n"
        f"مجموع درصد کاهش دمیج فعلی تو: {total_defense:.1f}٪\n"
        "هر تیکه تجهیزات یه بخش از بدنت رو محافظت می‌کنه و درصد دمیجی که ازت کم میشه رو کاهش میده\n\n"
        "🟢 قابل ساخت/ارتقا   🔴 پول کافی نداری   🔒 لول لازم رو نداری   🏆 حداکثر لول",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("equip_detail:"))
async def cb_equipment_detail(callback: CallbackQuery, user: User) -> None:
    equipment_id = callback.data.split(":", 1)[1]
    owned = await equipment_repo.get_user_equipment(user.user_id)
    current = next((e for e in owned if e["equipment_id"] == equipment_id), None)
    current_level = current["level"] if current else 0

    catalog = await equipment_repo.list_equipment_catalog()
    item = next((c for c in catalog if c["equipment_id"] == equipment_id), None)
    if item is None:
        await callback.answer("پیدا نشد", show_alert=True)
        return

    cost = _cost_for_level(current_level)
    required_level = item.get("required_level", 1)
    maxed = current_level >= EQUIPMENT_MAX_LEVEL
    locked_by_level = current_level == 0 and user.level < required_level

    base = item.get("defense_percent_base", 3.0)
    growth = item.get("defense_percent_growth", 1.2)
    current_defense = _defense_percent(base, growth, current_level)
    next_defense = _defense_percent(base, growth, current_level + 1) if not maxed else current_defense

    slot_label = SLOT_LABELS_FA.get(item["slot"], item["slot"])
    action_label = "ساخت" if current_level == 0 else "ارتقاء"

    text = (
        f"{item['emoji']} {item['name_fa']}\n\n"
        f"محل: {slot_label}\n"
        f"لول فعلی: {current_level}/{EQUIPMENT_MAX_LEVEL}\n"
        f"کاهش دمیج فعلی: {current_defense:.1f}٪\n"
    )

    if current_level == 0:
        text += f"لول لازم برای ساخت: {required_level}\nهزینه ساخت اولیه: {format_currency(cost)}💊"
    elif not maxed:
        text += (
            f"کاهش دمیج بعد از ارتقاء: {next_defense:.1f}٪\n"
            f"هزینه {action_label}: {format_currency(cost)}💊"
        )
    else:
        text += "🏆 این تجهیزات به حداکثر لول رسیده"

    if locked_by_level:
        text += f"\n\n🔒 لولت کافی نیست (لول تو: {user.level})"

    rows = []
    if not locked_by_level and not maxed:
        button_label = "✅ ساخت" if current_level == 0 else "✅ ارتقاء"
        rows.append(
            [InlineKeyboardButton(text=button_label, callback_data=f"equip_upgrade:{equipment_id}")]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:equipment")])
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("equip_upgrade:"))
async def cb_equipment_upgrade(callback: CallbackQuery, user: User) -> None:
    equipment_id = callback.data.split(":", 1)[1]
    owned = await equipment_repo.get_user_equipment(user.user_id)
    current = next((e for e in owned if e["equipment_id"] == equipment_id), None)
    current_level = current["level"] if current else 0

    catalog = await equipment_repo.list_equipment_catalog()
    item = next((c for c in catalog if c["equipment_id"] == equipment_id), None)
    if item is None:
        await callback.answer("پیدا نشد", show_alert=True)
        return

    required_level = item.get("required_level", 1)
    if current_level == 0 and user.level < required_level:
        await callback.answer(not_enough_level(required_level), show_alert=True)
        return

    if current_level >= EQUIPMENT_MAX_LEVEL:
        await callback.answer("🏆 این تجهیزات از قبل به حداکثر لول رسیده", show_alert=True)
        return

    cost = _cost_for_level(current_level)
    if user.tiriak_point < cost:
        await callback.answer(not_enough_money(), show_alert=True)
        return

    await user_repo.adjust_tiriak(user.user_id, -cost)
    await equipment_repo.upgrade_equipment(user.user_id, equipment_id, current_level + 1)
    label = "ساخته شد" if current_level == 0 else f"ارتقا یافت به لول {current_level + 1}"
    await callback.answer(f"✅ {label}", show_alert=True)
    await cb_equipment_detail(callback, user)
