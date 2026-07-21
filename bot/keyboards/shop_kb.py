from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.dog import DogBreed
from bot.database.models.weapon import Weapon
from bot.utils.formatting import format_currency

CURRENCY_ICON = {"tiriak": "💊"}


def shop_hub_keyboard() -> InlineKeyboardMarkup:
    """صفحه اصلی فروشگاه - بخش‌بندی شده (ساختمان‌ها جدا از فروشگاهه، از منوی اصلی در دسترسه)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔫 سلاح‌ها", callback_data="shop_cat:weapons")],
            [InlineKeyboardButton(text="🦺 زره و تجهیزات", callback_data="shop_cat:equipment")],
            [InlineKeyboardButton(text="🐶 سگ‌ها", callback_data="shop_cat:dogs")],
            [InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")],
        ]
    )


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
        "🟢 قابل خرید   🔴 پول کافی نداری   🔒 هنوز لول لازم رو نداری   ✅ قبلاً خریدی",
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
        lines.append(f"لول: {w.required_level} | قیمت: {price_label}")
        lines.append(f"قدرت: {int(w.damage * 0.85)} تا {int(w.damage * 1.15)} | سرعت: {speed_label}")
        lines.append(mark)
        lines.append("")

    return "\n".join(lines).rstrip()


def weapon_shop_keyboard(include_back_button: bool = True) -> InlineKeyboardMarkup:
    """کیبورد فروشگاه سلاح - فقط سه دکمه: خرید سلاح / خرید مهمات / بازگشت (بازگشت اختیاری، برای گروه نمایش داده نمیشه)"""
    rows = [
        [InlineKeyboardButton(text="✅ خرید سلاح", callback_data="weapon_buy_help")],
        [InlineKeyboardButton(text="🔄 خرید مهمات", callback_data="weapon_ammo_help")],
    ]
    if include_back_button:
        rows.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="shop_cat:weapons_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
