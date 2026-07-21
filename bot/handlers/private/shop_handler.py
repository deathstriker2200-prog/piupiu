from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database.models.user import User
from bot.database.repositories import dog_repo, weapon_repo
from bot.keyboards.common import back_keyboard
from bot.keyboards.shop_kb import (
    shop_hub_keyboard,
    weapon_shop_keyboard,
    weapon_shop_text,
)
from bot.services.dog_service import DogError, purchase_dog
from bot.services.shop_service import ShopError, purchase_ammo, purchase_weapon
from bot.texts.common_texts import not_enough_level, not_enough_money
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
        "برای خرید دستور زیر رو بفرست:\n\nخرید [اسم سلاح]\n\nمثلا: خرید کلاشنیکف",
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
    lines = [
        "🐶 فروشگاه سگ‌ها",
        "",
        "🟢 قابل خرید   🔴 پول کافی نداری   🔒 هنوز لول لازم رو نداری",
        "",
    ]
    for d in sorted(dogs, key=lambda x: x.power):
        can_afford = user.tiriak_point >= d.price
        if user.level < d.required_level:
            mark = "🔒"
        elif not can_afford:
            mark = "🔴"
        else:
            mark = "🟢"
        price_label = "رایگان" if d.price == 0 else f"{format_currency(d.price)}💊"
        lines.append(f"{d.emoji} {d.name_fa}")
        lines.append(f"لول: {d.required_level} | قیمت: {price_label}")
        lines.append(
            f"قدرت: {d.power} | سلامتی: {d.hp} | شانس دفاع: {int(d.defense_chance*100)}٪ | "
            f"درآمد ساعتی: {format_currency(d.income_per_hour)}TP"
        )
        lines.append(mark)
        lines.append("")

    text = "\n".join(lines).rstrip()
    text += "\n\nبرای خرید دستور زیر رو بفرست:\n\nخرید سگ [نژاد] [اسمی که میخوای بذاری]\n\nمثلا: خرید سگ گرگ کامبیز"

    await callback.message.edit_text(text, reply_markup=back_keyboard("menu:shop"))
    await callback.answer()


DOG_BREED_FA_NAME_TO_ID = {
    "ولگرد": "stray",
    "سگ ولگرد": "stray",
    "دوبرمن": "doberman",
    "گرگ": "wolf",
}


def _find_dog_breed_id(text: str) -> str | None:
    cleaned = " ".join(text.strip().split())
    if cleaned in DOG_BREED_FA_NAME_TO_ID:
        return DOG_BREED_FA_NAME_TO_ID[cleaned]
    for name, breed_id in DOG_BREED_FA_NAME_TO_ID.items():
        if name in cleaned:
            return breed_id
    return None


@router.message(lambda m: m.text and m.text.strip().startswith("خرید سگ"))
async def handle_dog_purchase_text(message: Message, user: User) -> None:
    rest = message.text.strip()[len("خرید سگ"):].strip()
    parts = rest.split()
    if len(parts) < 2:
        await message.reply(
            "برای خرید سگ دستور رو کامل بفرست:\n\nخرید سگ [نژاد] [اسم]\n\nمثلا: خرید سگ گرگ کامبیز"
        )
        return

    # آخرین کلمه اسم سگه، بقیه اسم نژاد (چون بعضی نژادها دو کلمه‌ای هستن مثل "سگ ولگرد")
    nickname = parts[-1]
    breed_text = " ".join(parts[:-1])
    breed_id = _find_dog_breed_id(breed_text)

    if breed_id is None:
        await message.reply("همچین نژادی نداریم، نژادهای موجود: ولگرد، دوبرمن، گرگ 🤔")
        return

    try:
        await purchase_dog(user.user_id, breed_id, nickname)
    except DogError as e:
        error = str(e)
        if error == "not_enough_money":
            await message.reply(not_enough_money())
        elif error.startswith("level_required:"):
            required = int(error.split(":", 1)[1])
            await message.reply(not_enough_level(required))
        elif error == "invalid_name":
            await message.reply("اسم سگ باید بین ۱ تا ۲۰ کاراکتر باشه")
        elif error == "name_taken":
            await message.reply("یه سگ دیگه از قبل همین اسم رو داره، یه اسم دیگه انتخاب کن")
        else:
            await message.reply("مشکلی پیش اومد، دوباره امتحان کن")
        return

    breed = await dog_repo.get_dog_breed(breed_id)
    breed_name = breed.name_fa if breed else "سگ"
    await message.reply(f"✅ یه {breed_name} خریدی و اسمش رو گذاشتی «{nickname}» 🐶")


