from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin:users"),
                InlineKeyboardButton(text="📢 ارسال همگانی", callback_data="admin:broadcast"),
            ],
            [
                InlineKeyboardButton(text="💊 دادن پول/XP/الماس", callback_data="admin:grant"),
                InlineKeyboardButton(text="🚫 بن/آن‌بن", callback_data="admin:ban"),
            ],
            [
                InlineKeyboardButton(text="🎁 دادن/حذف آیتم", callback_data="admin:items"),
                InlineKeyboardButton(text="📜 ساخت کوئست", callback_data="admin:create_quest"),
            ],
            [
                InlineKeyboardButton(text="🏪 مدیریت فروشگاه", callback_data="admin:shop"),
                InlineKeyboardButton(text="🏗 مدیریت ساختمان‌ها", callback_data="admin:buildings"),
            ],
            [
                InlineKeyboardButton(text="🏴 مدیریت تیم‌ها", callback_data="admin:teams"),
                InlineKeyboardButton(text="⚙️ تنظیم Cooldown/Damage/Drop", callback_data="admin:tuning"),
            ],
            [
                InlineKeyboardButton(text="📊 مشاهده آمار", callback_data="admin:stats"),
            ],
        ]
    )


def admin_confirm_action_keyboard(action_id: str) -> InlineKeyboardMarkup:
    """برای اقدامات حساس ادمین مثل بن کردن یا حذف آیتم - تایید سبز/لغو قرمز"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ تایید", callback_data=f"admin_confirm:{action_id}"),
                InlineKeyboardButton(text="❌ لغو", callback_data=f"admin_cancel:{action_id}"),
            ]
        ]
    )
