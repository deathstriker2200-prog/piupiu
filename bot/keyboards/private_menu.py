from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 پروفایل", callback_data="menu:profile"),
                InlineKeyboardButton(text="🎒 کوله", callback_data="menu:inventory"),
            ],
            [
                InlineKeyboardButton(text="🛒 فروشگاه", callback_data="menu:shop"),
                InlineKeyboardButton(text="🏦 بانک", callback_data="menu:bank"),
            ],
            [
                InlineKeyboardButton(text="🏗 ساختمان‌ها", callback_data="menu:buildings"),
                InlineKeyboardButton(text="🐕 سگ‌های من", callback_data="menu:my_dogs"),
            ],
            [
                InlineKeyboardButton(text="🏴 تیم", callback_data="menu:team"),
                InlineKeyboardButton(text="📜 کوئست‌ها", callback_data="menu:quests"),
            ],
            [
                InlineKeyboardButton(text="🏆 لیدربرد", callback_data="menu:leaderboard"),
                InlineKeyboardButton(text="➕ افزودن به گروه", callback_data="menu:add_to_group"),
            ],
        ]
    )
