"""
داده‌های اولیه ثابت بازی (کاتالوگ سلاح‌ها، سگ‌ها، غذا، تجهیزات، ساختمان‌ها)
با اجرای seed_all() این‌ها داخل دیتابیس درج میشن (اگه از قبل نباشن)
این تابع در استارتاپ ربات (یا یک بار دستی) فراخوانی میشه
"""

from bot.database.db import get_conn

WEAPONS = [
    # melee -- weapon_id, name_fa, emoji, category, damage, cooldown_sec, price, currency, req_level, needs_ammo, mag, reload, special
    ("fist", "مشت", "👊", "melee", 5, 15, 0, "tiriak", 1, 0, None, None, "سلاح پیش‌فرض همه بازیکن‌ها"),
    ("brass_knuckle", "پنجه بکس", "🥊", "melee", 8, 15, 300, "tiriak", 2, 0, None, None, None),
    ("knife", "چاقو", "🔪", "melee", 12, 20, 800, "tiriak", 3, 0, None, None, None),
    ("axe", "تبر", "🪓", "melee", 18, 30, 1500, "tiriak", 5, 0, None, None, None),
    ("sword", "شمشیر", "⚔", "melee", 22, 35, 2500, "tiriak", 7, 0, None, None, None),
    ("hammer", "چکش", "🔨", "melee", 20, 30, 2200, "tiriak", 6, 0, None, None, "شانس گیج کردن حریف"),
    ("saw", "اره", "🪚", "melee", 25, 40, 3000, "tiriak", 8, 0, None, None, None),
    ("katana", "کاتانا", "🗡", "melee", 35, 45, 6000, "tiriak", 12, 0, None, None, "شانس کریتیکال بالا"),
    # firearms
    ("colt", "کلت", "🔫", "firearm", 20, 25, 2000, "tiriak", 4, 1, 6, 10, None),
    ("deagle", "دزرت ایگل", "🦅", "firearm", 30, 30, 4000, "tiriak", 7, 1, 7, 12, None),
    ("uzi", "UZI", "🔫", "firearm", 28, 15, 5000, "tiriak", 8, 1, 25, 15, "شلیک سریع"),
    ("ak47", "AK47", "🪖", "firearm", 40, 20, 8000, "tiriak", 10, 1, 30, 18, None),
    ("m4", "M4", "🎯", "firearm", 42, 20, 9000, "both", 11, 1, 30, 18, None),
    ("shotgun", "شاتگان", "💥", "firearm", 50, 35, 10000, "tiriak", 13, 1, 8, 20, "دمیج بالا از فاصله نزدیک"),
    ("sniper", "اسنایپر", "🎯", "firearm", 65, 60, 15000, "diamond", 15, 1, 5, 25, "همیشه کریتیکال"),
    ("minigun", "مینی گان", "🔥", "firearm", 55, 40, 20000, "diamond", 18, 1, 100, 30, None),
    ("rpg", "RPG", "💣", "firearm", 80, 90, 30000, "diamond", 20, 1, 1, 40, "دمیج به گروه"),
    ("launcher", "لانچر", "🚀", "firearm", 100, 120, 50000, "diamond", 25, 1, 1, 50, "قدرتمندترین سلاح بازی"),
    # fun
    ("water_gun", "آب‌پاش", "💦", "fun", 1, 10, 100, "tiriak", 1, 0, None, None, "خیس کردن حریف 😂"),
    ("cucumber", "خیار", "🥒", "fun", 2, 10, 150, "tiriak", 1, 0, None, None, None),
    ("slipper", "دمپایی", "🩴", "fun", 3, 10, 200, "tiriak", 1, 0, None, None, "کلاسیک مامان‌ها"),
    ("spoon", "قاشق", "🥄", "fun", 1, 10, 100, "tiriak", 1, 0, None, None, None),
    ("broom", "جارو", "🧹", "fun", 4, 12, 250, "tiriak", 1, 0, None, None, None),
    ("brick", "آجر", "🧱", "fun", 6, 15, 400, "tiriak", 2, 0, None, None, "درد داره ولی خنده‌داره"),
]

DOGS = [
    # dog_id, name_fa, emoji, power, hp, defense_chance, income_per_hour, price, currency
    ("stray", "سگ ولگرد", "🐶", 5, 50, 0.10, 20, 500, "tiriak"),
    ("doberman", "دوبرمن", "🐕", 15, 100, 0.25, 60, 3000, "tiriak"),
    ("wolf", "گرگ", "🐺", 30, 180, 0.40, 150, 10000, "both"),
]

FOOD = [
    # food_id, name_fa, emoji, xp_amount, price, currency
    ("bone", "استخوان", "🦴", 10, 50, "tiriak"),
    ("meat", "گوشت", "🍖", 25, 150, "tiriak"),
    ("canned", "کنسرو", "🥫", 40, 300, "tiriak"),
    ("steak", "استیک", "🥩", 70, 600, "tiriak"),
]

EQUIPMENT = [
    # equipment_id, name_fa, emoji, slot
    ("vest", "جلیقه", "🦺", "vest"),
    ("helmet", "کلاه", "⛑", "helmet"),
    ("boots", "چکمه", "🥾", "boots"),
    ("gloves", "دستکش", "🧤", "gloves"),
]

BUILDINGS = [
    # building_id, name_fa, emoji, effect_type, base_value, value_growth
    ("mine", "معدن", "⛏", "income", 50, 1.15),
    ("company", "شرکت", "🏢", "fixed_income", 100, 1.10),
    ("factory", "کارخانه", "🏭", "income", 80, 1.12),
    ("greenhouse", "گلخانه", "🌿", "income", 40, 1.10),
    ("bank_building", "بانک", "💰", "bank_interest", 0.01, 1.05),
    ("warehouse", "انبار", "🏚", "storage_capacity", 500, 1.10),
    ("gang_hq", "گروهک", "🏴", "gang_damage", 0.02, 1.08),
    ("military_base", "پایگاه نظامی", "🎯", "combat_power", 0.03, 1.08),
]


async def seed_all() -> None:
    async with get_conn() as conn:
        await conn.executemany(
            """INSERT OR IGNORE INTO weapons
               (weapon_id, name_fa, emoji, category, damage, cooldown_sec, price, price_currency,
                required_level, needs_ammo, magazine_size, reload_sec, special_trait)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            WEAPONS,
        )
        await conn.executemany(
            """INSERT OR IGNORE INTO dogs_catalog
               (dog_id, name_fa, emoji, power, hp, defense_chance, income_per_hour, price, price_currency)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            DOGS,
        )
        await conn.executemany(
            """INSERT OR IGNORE INTO food_catalog (food_id, name_fa, emoji, xp_amount, price, price_currency)
               VALUES (?, ?, ?, ?, ?, ?)""",
            FOOD,
        )
        await conn.executemany(
            """INSERT OR IGNORE INTO equipment_catalog (equipment_id, name_fa, emoji, slot)
               VALUES (?, ?, ?, ?)""",
            EQUIPMENT,
        )
        await conn.executemany(
            """INSERT OR IGNORE INTO buildings_catalog
               (building_id, name_fa, emoji, effect_type, base_value, value_growth)
               VALUES (?, ?, ?, ?, ?, ?)""",
            BUILDINGS,
        )
        await conn.commit()
