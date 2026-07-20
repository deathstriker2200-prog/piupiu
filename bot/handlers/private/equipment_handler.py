from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import equipment_repo, user_repo
from bot.keyboards.common import back_keyboard
from bot.texts.common_texts import not_enough_money
from bot.utils.formatting import format_currency

router = Router(name="private_equipment")

EQUIPMENT_UPGRADE_BASE_COST = 800


def _cost_for_level(current_level: int) -> int:
    return EQUIPMENT_UPGRADE_BASE_COST * (current_level + 1)


@router.callback_query(lambda c: c.data == "menu:equipment" or c.data == "shop_cat:equipment")
async def cb_equipment_menu(callback: CallbackQuery, user: User) -> None:
    catalog = await equipment_repo.list_equipment_catalog()
    owned = await equipment_repo.get_user_equipment(user.user_id)
    levels = {e["equipment_id"]: e["level"] for e in owned}

    rows = []
    for item in catalog:
        level = levels.get(item["equipment_id"], 0)
        cost = _cost_for_level(level)
        mark = "✅" if user.tiriak_point >= cost else "🔒"
        action_label = "ساخت" if level == 0 else f"ارتقا به لول {level + 1}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"{mark} {item['emoji']} {item['name_fa']} (لول فعلی {level}) — "
                        f"{action_label}: {format_currency(cost)}💊"
                    ),
                    callback_data=f"equip_detail:{item['equipment_id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    await callback.message.edit_text(
        "🦺 تجهیزات - قیمت ساخت/ارتقای بعدی کنار هرکدوم نوشته شده",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("equip_detail:"))
async def cb_equipment_detail(callback: CallbackQuery, user: User) -> None:
    equipment_id = callback.data.split(":", 1)[1]
    owned = await equipment_repo.get_user_equipment(user.user_id)
    current_level = next((e["level"] for e in owned if e["equipment_id"] == equipment_id), 0)
    catalog = await equipment_repo.list_equipment_catalog()
    item = next((c for c in catalog if c["equipment_id"] == equipment_id), None)
    if item is None:
        await callback.answer("پیدا نشد", show_alert=True)
        return

    cost = _cost_for_level(current_level)
    action_label = "ساخت اولیه" if current_level == 0 else f"ارتقا به لول {current_level + 1}"

    text = (
        f"{item['emoji']} {item['name_fa']}\n\n"
        f"لول فعلی: {current_level}\n"
        f"هزینه {action_label}: {format_currency(cost)}💊"
    )

    button_label = "🛠 ساخت" if current_level == 0 else "⬆️ ارتقا"
    rows = [
        [InlineKeyboardButton(text=button_label, callback_data=f"equip_upgrade:{equipment_id}")],
        [InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:equipment")],
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("equip_upgrade:"))
async def cb_equipment_upgrade(callback: CallbackQuery, user: User) -> None:
    equipment_id = callback.data.split(":", 1)[1]
    owned = await equipment_repo.get_user_equipment(user.user_id)
    current_level = next((e["level"] for e in owned if e["equipment_id"] == equipment_id), 0)
    cost = _cost_for_level(current_level)

    if user.tiriak_point < cost:
        await callback.answer(not_enough_money(), show_alert=True)
        return

    await user_repo.adjust_tiriak(user.user_id, -cost)
    await equipment_repo.upgrade_equipment(user.user_id, equipment_id, current_level + 1)
    label = "ساخته شد" if current_level == 0 else f"ارتقا یافت به لول {current_level + 1}"
    await callback.answer(f"✅ {label}", show_alert=True)
    await cb_equipment_menu(callback, user)
