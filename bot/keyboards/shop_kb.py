from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.dog import DogBreed
from bot.database.models.weapon import Weapon
from bot.utils.formatting import format_currency

CURRENCY_ICON = {"tiriak": "💊"}


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


def _weapon_status_mark(user_level: int, required_level: int, can_afford: bool, owned: bool) -> str:
    if owned:
        return "✅"
    if user_level < required_level:
        return "🔒"
    if not can_afford:
        return "🔴"
    return "🟢"


def weapon_shop_text(
    weapons: list[Weapon], owned_ids: set[str], user_level: int, user_tiriak: int
) -> str:
    """
    متن کامل و یکجای فروشگاه سلاح - از ضعیف‌ترین تا قوی‌ترین سلاح
    هر سلاح با وضعیت (🟢 قابل خرید / 🔴 پول کافی نداری / 🔒 لول کافی نداری / ✅ قبلاً خریدی) نشون داده میشه
    """
    lines = [
        "🔫 فروشگاه سلاح‌ها",
        "",
        "🟢 قابل خرید   🔴 پول کافی نداری   🔒 هنوز Level لازم رو نداری   ✅ قبلاً خریدی",
        "",
    ]
    sorted_weapons = sorted(weapons, key=lambda w: w.damage)

    for w in sorted_weapons:
        owned = w.weapon_id in owned_ids
        can_afford = user_tiriak >= w.price
        mark = _weapon_status_mark(user_level, w.required_level, can_afford, owned)
        price_label = "رایگان" if w.price == 0 else f"{format_currency(w.price)}{CURRENCY_ICON.get(w.price_currency, '')}"
        speed_label = f"{w.cooldown_sec} ثانیه"

        lines.append(f"{w.emoji} {w.name_fa}")
        lines.append(f"Level: {w.required_level} | قیمت: {price_label}")
        lines.append(f"قدرت: {int(w.damage * 0.85)} تا {int(w.damage * 1.15)} | سرعت: {speed_label}")
        lines.append(mark)
        lines.append("")

    return "\n".join(lines).rstrip()


def weapon_shop_keyboard(include_back_button: bool = True) -> InlineKeyboardMarkup:
    """کیبورد فروشگاه سلاح - فقط سه دکمه: خرید سلاح / خرید مهمات / بازگشت (بازگشت اختیاری، برای گروه نمایش داده نمیشه)"""
    rows = [
        [InlineKeyboardButton(text="🛒 خرید سلاح", callback_data="weapon_buy_help")],
        [InlineKeyboardButton(text="🔄 خرید مهمات", callback_data="weapon_ammo_help")],
    ]
    if include_back_button:
        rows.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="shop_cat:weapons_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dog_list_keyboard(
    dogs: list[DogBreed], user_level: int, user_tiriak: int
) -> InlineKeyboardMarkup:
    """سگ‌ها بر اساس قدرت (power) مرتب میشن، ضعیف‌ترین اول"""
    rows = []
    sorted_dogs = sorted(dogs, key=lambda d: d.power)

    for d in sorted_dogs:
        can_afford = user_tiriak >= d.price
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
