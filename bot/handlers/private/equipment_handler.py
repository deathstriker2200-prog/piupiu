from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import equipment_repo, user_repo
from bot.keyboards.common import back_keyboard
from bot.texts.common_texts import not_enough_money

router = Router(name="private_equipment")

EQUIPMENT_UPGRADE_BASE_COST = 800


@router.callback_query(lambda c: c.data == "menu:equipment")
async def cb_equipment_menu(callback: CallbackQuery, user: User) -> None:
    catalog = await equipment_repo.list_equipment_catalog()
    owned = await equipment_repo.get_user_equipment(user.user_id)
    levels = {e["equipment_id"]: e["level"] for e in owned}

    rows = []
    for item in catalog:
        level = levels.get(item["equipment_id"], 0)
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{item['emoji']} {item['name_fa']} (لول {level})",
                    callback_data=f"equip_upgrade:{item['equipment_id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    await callback.message.edit_text(
        "🦺 تجهیزات - برای ارتقا لمس کن", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("equip_upgrade:"))
async def cb_equipment_upgrade(callback: CallbackQuery, user: User) -> None:
    equipment_id = callback.data.split(":", 1)[1]
    owned = await equipment_repo.get_user_equipment(user.user_id)
    current_level = next((e["level"] for e in owned if e["equipment_id"] == equipment_id), 0)
    cost = EQUIPMENT_UPGRADE_BASE_COST * (current_level + 1)

    if user.tiriak_point < cost:
        await callback.answer(not_enough_money(), show_alert=True)
        return

    await user_repo.adjust_tiriak(user.user_id, -cost)
    await equipment_repo.upgrade_equipment(user.user_id, equipment_id, current_level + 1)
    await callback.answer(f"✅ ارتقا موفق رفت لول {current_level + 1}", show_alert=True)
    await cb_equipment_menu(callback, user)
