from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import User
from bot.database.repositories import dog_repo
from bot.keyboards.common import back_keyboard
from bot.services.dog_service import DOG_ATTACK_COOLDOWN_SECONDS, DogError, feed_dog
from bot.texts.dog_texts import dog_fed, dog_full_already, dog_leveled_up
from bot.utils.formatting import format_seconds

router = Router(name="private_dog")


@router.callback_query(lambda c: c.data == "menu:my_dogs")
async def cb_my_dogs(callback: CallbackQuery, user: User) -> None:
    dogs = await dog_repo.get_user_dogs(user.user_id)
    if not dogs:
        await callback.message.edit_text(
            "هنوز سگی نداری برو از فروشگاه یکی بخر 🐶", reply_markup=back_keyboard("menu:main")
        )
        await callback.answer()
        return

    rows = []
    for d in dogs:
        breed = await dog_repo.get_dog_breed(d.dog_id)
        label = f"{breed.emoji if breed else '🐶'} {d.nickname or (breed.name_fa if breed else d.dog_id)} (لول {d.dog_level})"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"dog_manage:{d.id}")])
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])

    await callback.message.edit_text(
        "🐕 سگ‌های تو\n\nبرای حمله با یکی از این سگ‌ها تو گروه بنویس:\n[اسم سگ] بگیرش (ریپلای روی پیام هدف)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("dog_manage:"))
async def cb_dog_manage(callback: CallbackQuery, user: User) -> None:
    user_dog_id = int(callback.data.split(":", 1)[1])
    dog = await dog_repo.get_user_dog_by_id(user_dog_id)
    if dog is None or dog.user_id != user.user_id:
        await callback.answer("پیدا نشد", show_alert=True)
        return

    breed = await dog_repo.get_dog_breed(dog.dog_id)

    cooldown_line = "🟢 آماده حمله"
    if dog.attack_cooldown_until:
        from datetime import datetime

        cd_dt = datetime.fromisoformat(dog.attack_cooldown_until)
        if cd_dt > datetime.utcnow():
            seconds_left = int((cd_dt - datetime.utcnow()).total_seconds())
            cooldown_line = f"🕐 {format_seconds(seconds_left)} تا حمله بعدی مونده"

    text = (
        f"{breed.emoji if breed else '🐶'} {dog.nickname or (breed.name_fa if breed else '')}\n\n"
        f"نژاد: {breed.name_fa if breed else '-'}\n"
        f"لول: {dog.dog_level}\n"
        f"ایکس‌پی: {dog.dog_xp}\n"
        f"قدرت حمله: {dog.attack_damage_min} تا {dog.attack_damage_max} دمیج\n"
        f"کولدان حمله: {format_seconds(DOG_ATTACK_COOLDOWN_SECONDS)}\n"
        f"وضعیت: {cooldown_line}\n\n"
        f"برای حمله تو گروه بنویس (ریپلای روی پیام هدف):\n"
        f"«{dog.nickname or 'اسم سگت'} بگیرش»"
    )
    rows = [
        [InlineKeyboardButton(text="🍖 غذا دادن", callback_data=f"dog_feed_menu:{user_dog_id}")],
        [InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:my_dogs")],
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("dog_feed_menu:"))
async def cb_dog_feed_menu(callback: CallbackQuery, user: User) -> None:
    user_dog_id = int(callback.data.split(":", 1)[1])
    foods = await dog_repo.list_food()
    rows = [
        [
            InlineKeyboardButton(
                text=f"{f['emoji']} {f['name_fa']} (+{f['xp_amount']} ایکس‌پی)",
                callback_data=f"dog_feed:{user_dog_id}:{f['food_id']}",
            )
        ]
        for f in foods
    ]
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data=f"dog_manage:{user_dog_id}")])
    await callback.message.edit_text(
        "کدوم غذا رو بدم بهش؟", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("dog_feed:"))
async def cb_dog_feed(callback: CallbackQuery, user: User) -> None:
    _, user_dog_id_str, food_id = callback.data.split(":")
    user_dog_id = int(user_dog_id_str)

    try:
        result = await feed_dog(user.user_id, user_dog_id, food_id)
    except DogError as e:
        if str(e) == "dog_full":
            await callback.answer(dog_full_already(), show_alert=True)
        elif str(e) == "no_food_in_inventory":
            await callback.answer("این غذا رو نداری اول برو بخر 🛒", show_alert=True)
        else:
            await callback.answer("مشکلی پیش اومد", show_alert=True)
        return

    dog = await dog_repo.get_user_dog_by_id(user_dog_id)
    message_text = dog_fed(dog.nickname or "سگت", result["xp_gained"])
    if result["leveled_up"]:
        message_text += "\n" + dog_leveled_up(dog.nickname or "سگت", result["new_level"])

    await callback.answer(message_text, show_alert=True)
