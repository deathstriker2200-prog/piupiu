from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import building_repo
from bot.services.building_service import BuildingError, collect_income, upgrade_building
from bot.texts.common_texts import not_enough_money
from bot.utils.formatting import format_currency

router = Router(name="private_building")


@router.callback_query(lambda c: c.data == "menu:buildings")
async def cb_buildings_menu(callback: CallbackQuery, user: User) -> None:
    catalog = await building_repo.list_building_types()
    owned = await building_repo.get_user_buildings(user.user_id)
    levels = {b["building_id"]: b["level"] for b in owned}

    rows = []
    for b in catalog:
        level = levels.get(b.building_id, 0)
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{b.emoji} {b.name_fa} (لول {level})",
                    callback_data=f"building_detail:{b.building_id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    await callback.message.edit_text(
        "🏗 ساختمان‌های تو", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("building_detail:"))
async def cb_building_detail(callback: CallbackQuery, user: User) -> None:
    building_id = callback.data.split(":", 1)[1]
    building_type = await building_repo.get_building_type(building_id)
    owned = await building_repo.get_user_building(user.user_id, building_id)
    level = owned["level"] if owned else 0

    text = (
        f"{building_type.emoji} {building_type.name_fa}\n\n"
        f"لول فعلی: {level}\n"
        f"نوع اثر: {building_type.effect_type}"
    )

    rows = [
        [InlineKeyboardButton(text="⬆️ ارتقا", callback_data=f"building_upgrade:{building_id}")],
    ]
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
    except BuildingError:
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
