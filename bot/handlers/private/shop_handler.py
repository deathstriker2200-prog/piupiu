from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database.models.user import User
from bot.database.repositories import dog_repo, weapon_repo
from bot.keyboards.common import back_keyboard, confirm_cancel_keyboard
from bot.keyboards.shop_kb import (
    dog_list_keyboard,
    shop_hub_keyboard,
    weapon_shop_keyboard,
    weapon_shop_text,
)
from bot.services.dog_service import DogError, purchase_dog
from bot.services.shop_service import ShopError, purchase_ammo, purchase_weapon
from bot.texts.common_texts import not_enough_level, not_enough_money
from bot.texts.dog_texts import dog_purchased
from bot.utils.formatting import format_currency, format_seconds
from bot.utils.weapon_names import find_weapon_id_by_fa_name

router = Router(name="private_shop")


async def build_weapon_shop_text(user: User) -> str:
    weapons = await weapon_repo.list_weapons()
    owned = await weapon_repo.get_user_weapons(user.user_id)
    owned_ids = {w["weapon_id"] for w in owned}
    return weapon_shop_text(weapons, owned_ids, user.level, user.tiriak_point)


@router.callback_query(lambda c: c.data == "menu:shop" or c.data in ("shop_cat:weapons_back", "shop_cat:dogs_back"))
async def cb_shop_hub(callback: CallbackQuery, user: User) -> None:
    await callback.message.edit_text(
        "🛒 فروشگاه - یه بخش رو انتخاب کن", reply_markup=shop_hub_keyboard()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "shop_cat:weapons" or c.data == "menu:shop_weapons")
async def cb_shop_weapons(callback: CallbackQuery, user: User) -> None:
    text = await build_weapon_shop_text(user)
    await callback.message.edit_text(text, reply_markup=weapon_shop_keyboard(include_back_button=True))
    await callback.answer()


@router.callback_query(lambda c: c.data == "weapon_buy_help")
async def cb_weapon_buy_help(callback: CallbackQuery, user: User) -> None:
    await callback.answer(
        "برای خرید، دستور زیر رو بفرست:\n\nخرید کلاشنیکف\n\nیا\n\nخرید آرپی‌جی\n\nیا\n\nخرید شاتگان",
        show_alert=True,
    )


@router.callback_query(lambda c: c.data == "weapon_ammo_help")
async def cb_weapon_ammo_help(callback: CallbackQuery, user: User) -> None:
    await callback.answer(
        "برای خرید مهمات، دستور زیر رو بفرست:\n\nمهمات کلاشنیکف\n\nیا\n\nخرید مهمات آرپی‌جی",
        show_alert=True,
    )


@router.message(lambda m: m.text and m.text.strip().startswith("خرید مهمات"))
async def handle_ammo_purchase_text(message: Message, user: User) -> None:
    raw_name = message.text.strip()[len("خرید مهمات"):].strip()
    await _do_ammo_purchase(message, user, raw_name)


@router.message(lambda m: m.text and m.text.strip().startswith("مهمات"))
async def handle_ammo_purchase_text_short(message: Message, user: User) -> None:
    raw_name = message.text.strip()[len("مهمات"):].strip()
    await _do_ammo_purchase(message, user, raw_name)


@router.message(lambda m: m.text and m.text.strip().startswith("خرید"))
async def handle_weapon_purchase_text(message: Message, user: User) -> None:
    raw_name = message.text.strip()[len("خرید"):].strip()
    weapon_id = find_weapon_id_by_fa_name(raw_name)
    if weapon_id is None:
        await message.reply("همچین سلاحی تو فروشگاه نیست، اسمش رو درست بنویس مثلا «خرید کلاشنیکف» 🤔")
        return

    try:
        await purchase_weapon(user.user_id, weapon_id)
    except ShopError as e:
        await _reply_shop_error(message, str(e))
        return

    weapon = await weapon_repo.get_weapon(weapon_id)
    name = weapon.name_fa if weapon else raw_name
    await message.reply(f"✅ «{name}» رو خریدی و تجهیز شد، بزن بریم 🔫")


async def _do_ammo_purchase(message: Message, user: User, raw_name: str) -> None:
    weapon_id = find_weapon_id_by_fa_name(raw_name)
    if weapon_id is None:
        await message.reply("همچین سلاحی تو فروشگاه نیست، اسمش رو درست بنویس مثلا «مهمات کلاشنیکف» 🤔")
        return

    try:
        price = await purchase_ammo(user.user_id, weapon_id)
    except ShopError as e:
        await _reply_shop_error(message, str(e))
        return

    weapon = await weapon_repo.get_weapon(weapon_id)
    name = weapon.name_fa if weapon else raw_name
    await message.reply(f"🔄 مهمات «{name}» شارژ شد ({format_currency(price)} تریاک‌پوینت پرداخت کردی)")


async def _reply_shop_error(message: Message, error: str) -> None:
    if error == "already_owned":
        await message.reply("این سلاح رو قبلا خریدی")
    elif error == "not_owned":
        await message.reply("اول باید خود سلاح رو بخری، بعد براش مهمات بخر")
    elif error == "not_enough_money":
        await message.reply(not_enough_money())
    elif error.startswith("level_required:"):
        level = int(error.split(":", 1)[1])
        await message.reply(not_enough_level(level))
    elif error.startswith("ammo_cooldown:"):
        seconds = int(error.split(":", 1)[1])
        await message.reply(f"🕐 هنوز {format_seconds(seconds)} مونده تا بتونی دوباره مهمات این سلاح رو بخری")
    else:
        await message.reply("مشکلی پیش اومد، دوباره امتحان کن")


@router.callback_query(lambda c: c.data == "shop_cat:dogs" or c.data == "menu:shop_dogs")
async def cb_shop_dogs(callback: CallbackQuery, user: User) -> None:
    dogs = await dog_repo.list_dog_breeds()
    await callback.message.edit_text(
        "🐶 سگ‌ها - بر اساس قدرت مرتب شدن\n"
        "✅ = می‌تونی بخری   🔒 = پول کافی نیست   ❌ = لولت کافی نیست",
        reply_markup=dog_list_keyboard(dogs, user.level, user.tiriak_point),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("dog_info:"))
async def cb_dog_info(callback: CallbackQuery, user: User) -> None:
    dog_id = callback.data.split(":", 1)[1]
    breed = await dog_repo.get_dog_breed(dog_id)
    if breed is None:
        await callback.answer("پیدا نشد", show_alert=True)
        return

    text = (
        f"{breed.emoji} {breed.name_fa}\n\n"
        f"قدرت: {breed.power}\n"
        f"HP: {breed.hp}\n"
        f"شانس دفاع: {int(breed.defense_chance * 100)}%\n"
        f"درآمد ساعتی: {breed.income_per_hour}\n"
        f"قیمت: {format_currency(breed.price)} تریاک‌پوینت\n"
        f"لول لازم: {breed.required_level}"
    )
    if user.level < breed.required_level:
        text += f"\n\n❌ لولت کافی نیست (لول تو: {user.level})"
        await callback.message.edit_text(text, reply_markup=back_keyboard("shop_cat:dogs"))
        await callback.answer()
        return

    await callback.message.edit_text(
        text,
        reply_markup=confirm_cancel_keyboard(
            confirm_callback=f"dog_buy:{dog_id}", cancel_callback="shop_cat:dogs",
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
        error = str(e)
        if error == "not_enough_money":
            await callback.answer(not_enough_money(), show_alert=True)
        elif error.startswith("level_required:"):
            required = int(error.split(":", 1)[1])
            await callback.answer(not_enough_level(required), show_alert=True)
        else:
            await callback.answer("مشکلی پیش اومد", show_alert=True)
        return

    breed = await dog_repo.get_dog_breed(dog_id)
    await callback.message.edit_text(
        dog_purchased(breed.name_fa if breed else "سگ"), reply_markup=back_keyboard("menu:main")
    )
    await callback.answer()


