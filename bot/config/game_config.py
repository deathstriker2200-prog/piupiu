"""
مقادیر پایه بازی
این مقادیر پیش‌فرض هستن و از طریق پنل ادمین قابل تغییر خواهند بود
(مقادیر تغییر یافته داخل جدول settings در دیتابیس ذخیره میشن و این فایل فقط fallback هست)
"""

STARTING_HP = 200
STARTING_TIRIAK_POINT = 500
STARTING_LEVEL = 1

DEATH_RESPAWN_SECONDS = 10 * 60          # 10 دقیقه
JAIL_SECONDS = 15 * 60                   # 15 دقیقه
DOG_FEED_COOLDOWN_SECONDS = 2 * 60 * 60  # 2 ساعت

THEFT_SUCCESS_CHANCE = 0.30

XP_PER_LEVEL_BASE = 60
XP_PER_LEVEL_GROWTH = 1.22  # هر لول مقدار XP لازم به‌صورت نمایی بیشتر میشه (اوایل سریع، بعد سخت)

HP_GAIN_PER_LEVEL = 5
DAMAGE_GAIN_PER_LEVEL = 1

BANK_BASE_CAPACITY = 1000
BANK_UPGRADE_CAPACITY_STEP = 500
BANK_INTEREST_RATE = 0.01  # درصد سود روزانه بانک ساختمانی (متفاوت از حساب شخصی)

WEAPON_CATEGORIES = ("melee", "firearm", "fun")

DEFAULT_WEAPON_ID = "water_gun"  # تفنگ آب‌پاش - سلاح پیش‌فرض و جایگزین خودکار بعد از اتمام مهمات

KILL_TIRIAK_BONUS = 200  # جایزه ثابت تریاک‌پوینت با هر کشتن، جدا از سرقت درصدی
AMMO_REPURCHASE_COOLDOWN_SECONDS = 60  # بعد از اتمام مهمات یک دقیقه صبر برای خرید دوباره مهمات همون سلاح
