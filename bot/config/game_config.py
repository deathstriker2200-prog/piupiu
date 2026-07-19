"""
مقادیر پایه بازی
این مقادیر پیش‌فرض هستن و از طریق پنل ادمین قابل تغییر خواهند بود
(مقادیر تغییر یافته داخل جدول settings در دیتابیس ذخیره میشن و این فایل فقط fallback هست)
"""

STARTING_HP = 100
STARTING_TIRIAK_POINT = 500
STARTING_LEVEL = 1

DEATH_RESPAWN_SECONDS = 5 * 60          # 5 دقیقه
JAIL_SECONDS = 15 * 60                   # 15 دقیقه
DOG_FEED_COOLDOWN_SECONDS = 2 * 60 * 60  # 2 ساعت

THEFT_SUCCESS_CHANCE = 0.30

XP_PER_LEVEL_BASE = 100
XP_PER_LEVEL_GROWTH = 1.15  # هر لول مقدار XP لازم بیشتر میشه

HP_GAIN_PER_LEVEL = 5
DAMAGE_GAIN_PER_LEVEL = 1

BANK_BASE_CAPACITY = 1000
BANK_UPGRADE_CAPACITY_STEP = 500
BANK_INTEREST_RATE = 0.01  # درصد سود روزانه بانک ساختمانی (متفاوت از حساب شخصی)

WEAPON_CATEGORIES = ("melee", "firearm", "fun")

DEFAULT_WEAPON_ID = "fist"  # مشت - سلاح پیش‌فرض همه بازیکن‌ها بدون خرید
