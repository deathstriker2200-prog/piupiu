"""
کیبوردهای مشترک بین همه بخش‌های ربات

نکته مهم درباره رنگ دکمه‌ها:
تلگرام Bot API اجازه نمیده رنگ دکمه‌های inline keyboard رو کنترل کنیم
(همیشه استایل پیش‌فرض کلاینت کاربر رو دارن، مثلاً خاکستری یا آبی بسته به تم)
برای شبیه‌سازی حس "قبول = سبز" و "رد = قرمز" همه‌جای ربات
از یک پیشوند ایموجی ثابت استفاده می‌کنیم: ✅ برای قبول/تایید و ❌ برای رد/انصراف
این تابع‌ها این الگو رو یک‌جا نگه می‌دارن تا همه‌جای پروژه یکدست باشه
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CONFIRM_PREFIX = "✅"
CANCEL_PREFIX = "❌"


def confirm_cancel_keyboard(
    confirm_callback: str,
    cancel_callback: str,
    confirm_text: str = "قبول",
    cancel_text: str = "انصراف",
) -> InlineKeyboardMarkup:
    """کیبورد استاندارد قبول (✅ سبزوش) / انصراف (❌ قرمزوش) برای هر جای ربات که نیاز به تایید داره
    مثلا: دزدی, درخواست عضویت تیم, خرید آیتم گرون, حذف آیتم توسط ادمین
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{CONFIRM_PREFIX} {confirm_text}", callback_data=confirm_callback
                ),
                InlineKeyboardButton(
                    text=f"{CANCEL_PREFIX} {cancel_text}", callback_data=cancel_callback
                ),
            ]
        ]
    )


def accept_reject_keyboard(
    accept_callback: str,
    reject_callback: str,
) -> InlineKeyboardMarkup:
    """کیبورد قبول/رد درخواست (مثلا درخواست عضویت تیم برای لیدر تیم)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{CONFIRM_PREFIX} قبول", callback_data=accept_callback),
                InlineKeyboardButton(text=f"{CANCEL_PREFIX} رد", callback_data=reject_callback),
            ]
        ]
    )


def back_keyboard(back_callback: str, text: str = "🔙 برگشت") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=back_callback)]]
    )
