from aiogram import Router
from aiogram.types import CallbackQuery

from bot.database.models.user import User
from bot.database.repositories import dog_repo, weapon_repo
from bot.keyboards.common import back_keyboard, confirm_cancel_keyboard
from bot.keyboards.shop_kb import (
    dog_list_keyboard,
    weapon_detail_keyboard,
    weapon_list_keyboard,
)
from bot.services.dog_service import DogError, purchase_dog
from bot.services.shop_service import ShopError, equip_weapon, purchase_weapon
from bot.texts.common_texts import not_enough_level, not_enough_money
from bot.texts.dog_texts import dog_purchased
from bot.utils.formatting import format_currency

router = Router(name="private_shop")


@router.callback_query(lambda c: c.data == "menu:shop_weapons")
async def cb_shop_weapons(callback: CallbackQuery, user: User) -> None:
    weapons = await weapon_repo.list_weapons()
    owned = await weapon_repo.get_user_weapons(user.user_id)
    owned_ids = {w["weapon_id"] for w in owned}
    await callback.message.edit_text(
        "🔫 فروشگاه سلاح یکیشو انتخاب کن ببین چیه", reply_markup=weapon_list_keyboard(weapons, owned_ids)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("weapon_info:"))
async def cb_weapon_info(callback: CallbackQuery, user: User) -> None:
    weapon_id = callback.data.split(":", 1)[1]
    weapon = await weapon_repo.get_weapon(weapon_id)
    if weapon is None:
        await callback.answer("سلاح پیدا نشد", show_alert=True)
        return

    owned = await weapon_repo.user_owns_weapon(user.user_id, weapon_id)
    price_label = {"tiriak": "تریاک‌پوینت", "diamond": "الماس", "both": "تریاک‌پوینت + الماس"}[
        weapon.price_currency
    ]

    text = (
        f"{weapon.emoji} {weapon.name_fa}\n\n"
        f"Damage: {weapon.damage}\n"
        f"Cooldown: {weapon.cooldown_sec} ثانیه\n"
        f"قیمت: {format_currency(weapon.price)} {price_label}\n"
        f"لول لازم: {weapon.required_level}\n"
    )
    if weapon.needs_ammo:
        text += f"خشاب: {weapon.magazine_size} | Reload: {weapon.reload_sec} ثانیه\n"
    if weapon.special_trait:
        text += f"✨ {weapon.special_trait}\n"
    if owned:
        text += "\n✔️ این سلاح رو داری"

    can_afford = user.tiriak_point >= weapon.price if weapon.price_currency != "diamond" else user.diamond >= weapon.price
    await callback.message.edit_text(
        text, reply_markup=weapon_detail_keyboard(weapon_id, owned, can_afford)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("weapon_buy:"))
async def cb_weapon_buy(callback: CallbackQuery, user: User) -> None:
    weapon_id = callback.data.split(":", 1)[1]
    try:
        await purchase_weapon(user.user_id, weapon_id)
    except ShopError as e:
        await _handle_shop_error(callback, str(e))
        return

    await callback.answer("✅ خریدی مبارک باشه", show_alert=True)
    await cb_shop_weapons(callback, user)


@router.callback_query(lambda c: c.data and c.data.startswith("weapon_equip:"))
async def cb_weapon_equip(callback: CallbackQuery, user: User) -> None:
    weapon_id = callback.data.split(":", 1)[1]
    try:
        await equip_weapon(user.user_id, weapon_id)
    except ShopError:
        await callback.answer("مشکلی پیش اومد", show_alert=True)
        return
    await callback.answer("🔧 تجهیز شد آماده جنگی", show_alert=True)


@router.callback_query(lambda c: c.data == "menu:shop_dogs")
async def cb_shop_dogs(callback: CallbackQuery, user: User) -> None:
    dogs = await dog_repo.list_dog_breeds()
    await callback.message.edit_text("🐶 فروشگاه سگ یکیو انتخاب کن", reply_markup=dog_list_keyboard(dogs))
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("dog_info:"))
async def cb_dog_info(callback: CallbackQuery, user: User) -> None:
    dog_id = callback.data.split(":", 1)[1]
    breed = await dog_repo.get_dog_breed(dog_id)
    if breed is None:
        await callback.answer("پیدا نشد", show_alert=True)
        return

    price_label = "الماس" if breed.price_currency == "diamond" else "تریاک‌پوینت"
    text = (
        f"{breed.emoji} {breed.name_fa}\n\n"
        f"قدرت: {breed.power}\n"
        f"HP: {breed.hp}\n"
        f"شانس دفاع: {int(breed.defense_chance * 100)}%\n"
        f"درآمد ساعتی: {breed.income_per_hour}\n"
        f"قیمت: {format_currency(breed.price)} {price_label}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=confirm_cancel_keyboard(
            confirm_callback=f"dog_buy:{dog_id}", cancel_callback="menu:shop_dogs",
            confirm_text="خرید",
        ),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("dog_buy:"))
async def cb_dog_buy(callback: CallbackQuery, user: User) -> None:
    dog_id = callback.data.split(":", 1)[1]
    try:
        await purchase_dog(user.user_id, dog_id)
    except DogError as e:
        if str(e) == "not_enough_money":
            await callback.answer(not_enough_money(), show_alert=True)
        else:
            await callback.answer("مشکلی پیش اومد", show_alert=True)
        return

    breed = await dog_repo.get_dog_breed(dog_id)
    await callback.message.edit_text(
        dog_purchased(breed.name_fa if breed else "سگ"), reply_markup=back_keyboard("menu:main")
    )
    await callback.answer()


async def _handle_shop_error(callback: CallbackQuery, error: str) -> None:
    if error == "already_owned":
        await callback.answer("این سلاح رو قبلا خریدی", show_alert=True)
    elif error == "not_enough_money":
        await callback.answer(not_enough_money(), show_alert=True)
    elif error == "not_enough_diamond":
        await callback.answer("الماس کافی نداری 💎", show_alert=True)
    elif error.startswith("level_required:"):
        level = int(error.split(":", 1)[1])
        await callback.answer(not_enough_level(level), show_alert=True)
    else:
        await callback.answer("مشکلی پیش اومد", show_alert=True)
