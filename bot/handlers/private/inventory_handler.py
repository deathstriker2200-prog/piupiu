from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import dog_repo, weapon_repo
from bot.keyboards.common import back_keyboard
from bot.services.shop_service import ShopError, equip_weapon
from bot.services.shop_service import reload_weapon as reload_weapon_service

router = Router(name="private_inventory")


@router.callback_query(lambda c: c.data == "menu:inventory")
async def cb_inventory(callback: CallbackQuery, user: User) -> None:
    owned_weapons = await weapon_repo.get_user_weapons(user.user_id)
    food_items = await dog_repo.list_food()
    # فقط غذاهایی که واقعا تو کوله‌شونه رو نشون بده
    owned_food_rows = []
    from bot.database.db import get_conn

    async with get_conn() as conn:
        cursor = await conn.execute(
            """SELECT ufi.quantity, fc.name_fa, fc.emoji FROM user_food_inventory ufi
               JOIN food_catalog fc ON ufi.food_id = fc.food_id
               WHERE ufi.user_id = ? AND ufi.quantity > 0""",
            (user.user_id,),
        )
        owned_food_rows = await cursor.fetchall()

    lines = ["🎒 کوله تو\n"]

    if owned_weapons:
        lines.append("🔫 سلاح‌ها:")
        for w in owned_weapons:
            equipped_mark = "⭐" if w["is_equipped"] else ""
            ammo_line = f" | 🔹 تیر: {w['ammo_current']}" if w.get("category") == "firearm" else ""
            lines.append(f"{w['emoji']} {w['name_fa']} {equipped_mark}{ammo_line}")
        lines.append("")
    else:
        lines.append("🔫 هنوز سلاحی نداری\n")

    if owned_food_rows:
        lines.append("🍖 غذا:")
        for f in owned_food_rows:
            lines.append(f"{f['emoji']} {f['name_fa']} × {f['quantity']}")
    else:
        lines.append("🍖 غذایی تو کوله نداری")

    # دکمه‌های انتخاب سلاح برای تجهیز کردن مستقیم از کوله
    rows = []
    for w in owned_weapons:
        if w["is_equipped"]:
            continue
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🔧 تجهیز {w['emoji']} {w['name_fa']}",
                    callback_data=f"inv_equip:{w['weapon_id']}",
                )
            ]
        )

    # اگه سلاح فعلی تجهیزشده نیاز به تیر داره، دکمه Reload هم نشون بده
    equipped = next((w for w in owned_weapons if w["is_equipped"]), None)
    if equipped and equipped.get("category") == "firearm":
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🔄 Reload {equipped['name_fa']}",
                    callback_data=f"inv_reload:{equipped['weapon_id']}",
                )
            ]
        )

    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])

    await callback.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("inv_equip:"))
async def cb_inventory_equip(callback: CallbackQuery, user: User) -> None:
    weapon_id = callback.data.split(":", 1)[1]
    try:
        await equip_weapon(user.user_id, weapon_id)
    except ShopError:
        await callback.answer("مشکلی پیش اومد", show_alert=True)
        return
    await callback.answer("🔧 تجهیز شد", show_alert=True)
    await cb_inventory(callback, user)


@router.callback_query(lambda c: c.data and c.data.startswith("inv_reload:"))
async def cb_inventory_reload(callback: CallbackQuery, user: User) -> None:
    weapon_id = callback.data.split(":", 1)[1]
    try:
        await reload_weapon_service(user.user_id, weapon_id)
    except ShopError:
        await callback.answer("مشکلی پیش اومد", show_alert=True)
        return
    await callback.answer("🔄 خشاب پر شد", show_alert=True)
    await cb_inventory(callback, user)
