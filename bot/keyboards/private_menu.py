from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 پروفایل", callback_data="menu:profile"),
                InlineKeyboardButton(text="🎒 کوله", callback_data="menu:inventory"),
            ],
            [
                InlineKeyboardButton(text="🔫 فروشگاه سلاح", callback_data="menu:shop_weapons"),
                InlineKeyboardButton(text="🐶 فروشگاه سگ", callback_data="menu:shop_dogs"),
            ],
            [
                InlineKeyboardButton(text="🏦 بانک", callback_data="menu:bank"),
                InlineKeyboardButton(text="🏗 ساختمان‌ها", callback_data="menu:buildings"),
            ],
            [
                InlineKeyboardButton(text="🦺 تجهیزات", callback_data="menu:equipment"),
                InlineKeyboardButton(text="🐕 سگ‌های من", callback_data="menu:my_dogs"),
            ],
            [
                InlineKeyboardButton(text="🏴 تیم", callback_data="menu:team"),
                InlineKeyboardButton(text="📜 کوئست‌ها", callback_data="menu:quests"),
            ],
            [
                InlineKeyboardButton(text="🏆 لیدربرد", callback_data="menu:leaderboard"),
            ],
        ]
    )
