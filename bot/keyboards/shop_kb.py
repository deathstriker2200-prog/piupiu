from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.weapon import Weapon
from bot.database.models.dog import DogBreed


def weapon_list_keyboard(weapons: list[Weapon], owned_ids: set[str]) -> InlineKeyboardMarkup:
    rows = []
    for w in weapons:
        mark = "✔️" if w.weapon_id in owned_ids else ""
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{w.emoji} {w.name_fa} {mark}",
                    callback_data=f"weapon_info:{w.weapon_id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def weapon_detail_keyboard(weapon_id: str, owned: bool, can_afford: bool) -> InlineKeyboardMarkup:
    rows = []
    if not owned and can_afford:
        rows.append(
            [InlineKeyboardButton(text="✅ خرید", callback_data=f"weapon_buy:{weapon_id}")]
        )
    elif owned:
        rows.append(
            [InlineKeyboardButton(text="🔧 تجهیز کردن", callback_data=f"weapon_equip:{weapon_id}")]
        )
    rows.append([InlineKeyboardButton(text="❌ بستن", callback_data="menu:shop_weapons")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dog_list_keyboard(dogs: list[DogBreed]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{d.emoji} {d.name_fa}", callback_data=f"dog_info:{d.dog_id}")]
        for d in dogs
    ]
    rows.append([InlineKeyboardButton(text="🔙 برگشت", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
