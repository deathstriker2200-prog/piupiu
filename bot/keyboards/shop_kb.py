from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.dog import DogBreed
from bot.database.models.weapon import Weapon
from bot.utils.formatting import format_currency

CURRENCY_ICON = {"tiriak": "💊", "diamond": "💎", "both": "💊💎"}


def shop_hub_keyboard() -> InlineKeyboardMarkup:
    """صفحه اصلی فروشگاه - بخش‌بندی شده"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔫 سلاح‌ها", callback_data="shop_cat:weapons")],
            [InlineKeyboardButton(text="🦺 زره و تجهیزات", callback_data="shop_cat:equipment")],
            [InlineKeyboardButton(text="🐶 سگ‌ها", callback_data="shop_cat:dogs")],
            [InlineKeyboardButton(text="🏗 ساختمان‌ها", callback_data="shop_cat:buildings")],
            [InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")],
        ]
    )


def _lock_mark(user_level: int, required_level: int, can_afford: bool) -> str:
    if user_level < required_level:
        return "❌"
    if not can_afford:
        return "🔒"
    return "✅"


def weapon_list_keyboard(
    weapons: list[Weapon], owned_ids: set[str], user_level: int, user_tiriak: int, user_diamond: int
) -> InlineKeyboardMarkup:
    """
    هر سلاح رو با قیمت و لول لازم تو خود دکمه نشون میده
    مرتب‌شده بر اساس دسته (melee/firearm/fun) و بعد قیمت، ارزون‌ترین اول
    """
    rows = []
    sorted_weapons = sorted(weapons, key=lambda w: (w.category, w.price))

    for w in sorted_weapons:
        if w.weapon_id in owned_ids:
            mark = "🎒"  # تو کوله‌ات هست
        else:
            can_afford = (
                user_diamond >= w.price if w.price_currency == "diamond" else user_tiriak >= w.price
            )
            mark = _lock_mark(user_level, w.required_level, can_afford)

        price_label = f"{format_currency(w.price)}{CURRENCY_ICON.get(w.price_currency, '')}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{mark} {w.emoji} {w.name_fa} — {price_label} (لول {w.required_level})",
                    callback_data=f"weapon_info:{w.weapon_id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="shop_cat:weapons_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def weapon_detail_keyboard(weapon_id: str, owned: bool, can_buy: bool) -> InlineKeyboardMarkup:
    rows = []
    if not owned and can_buy:
        rows.append(
            [InlineKeyboardButton(text="✅ خرید", callback_data=f"weapon_buy:{weapon_id}")]
        )
    elif owned:
        rows.append(
            [InlineKeyboardButton(text="🔧 تجهیز کردن", callback_data=f"weapon_equip:{weapon_id}")]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="shop_cat:weapons")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dog_list_keyboard(
    dogs: list[DogBreed], user_level: int, user_tiriak: int, user_diamond: int
) -> InlineKeyboardMarkup:
    """سگ‌ها بر اساس قدرت (power) مرتب میشن، ضعیف‌ترین اول"""
    rows = []
    sorted_dogs = sorted(dogs, key=lambda d: d.power)

    for d in sorted_dogs:
        can_afford = (
            user_diamond >= d.price if d.price_currency == "diamond" else user_tiriak >= d.price
        )
        mark = _lock_mark(user_level, 1, can_afford)  # سگ‌ها فعلا محدودیت لول ندارن
        price_label = f"{format_currency(d.price)}{CURRENCY_ICON.get(d.price_currency, '')}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{mark} {d.emoji} {d.name_fa} — {price_label} (قدرت {d.power})",
                    callback_data=f"dog_info:{d.dog_id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="shop_cat:dogs_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
