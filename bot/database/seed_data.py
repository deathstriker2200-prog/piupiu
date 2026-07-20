"""
داده‌های اولیه ثابت بازی (کاتالوگ سلاح‌ها، سگ‌ها، غذا، تجهیزات، ساختمان‌ها)
با اجرای seed_all() این‌ها داخل دیتابیس درج میشن (اگه از قبل نباشن)
این تابع در استارتاپ ربات (یا یک بار دستی) فراخوانی میشه
"""

from bot.database.db import get_conn

WEAPONS = [
    # weapon_id, name_fa, emoji, category, damage(base), cooldown_sec, price, currency,
    # req_level, needs_ammo, mag, reload, special
    # damage پایه طوری تنظیم شده که با ضرب رندوم 0.85-1.15 داخل combat_service تقریبا همون بازه دمیج بشه
    ("water_gun", "تفنگ آب‌پاش", "💦", "fun", 13, 1, 0, "tiriak", 1, 0, None, None, "سلاح پیش‌فرض رایگان، کمی قوی‌تر شده تا تازه‌کارها ضعیف نباشن"),
    ("knife", "چاقو", "🔪", "melee", 16, 3, 450, "tiriak", 2, 0, None, None, None),
    ("colt", "کلت", "🔫", "firearm", 22, 5, 1500, "tiriak", 4, 0, None, None, None),
    ("shotgun", "شاتگان", "💥", "firearm", 39, 8, 4000, "tiriak", 7, 0, None, None, "دمیج بالا از فاصله نزدیک"),
    ("ak47", "کلاشنیکف", "🪖", "firearm", 55, 6, 8000, "tiriak", 10, 1, 30, 20, None),
    ("m4", "ام۴", "🎯", "firearm", 65, 5, 12000, "tiriak", 13, 1, 30, 18, None),
    ("sniper", "اسنایپر", "🎯", "firearm", 100, 15, 20000, "tiriak", 17, 1, 5, 30, "همیشه کریتیکال"),
    ("rpg", "آرپی‌جی", "💣", "firearm", 180, 30, 35000, "tiriak", 22, 1, 1, 45, "قدرتمندترین سلاح بازی"),
]

OLD_WEAPON_IDS_TO_REMOVE = [
    "fist", "brass_knuckle", "axe", "sword", "hammer", "saw", "katana",
    "deagle", "uzi", "minigun", "launcher", "cucumber", "slipper", "spoon", "broom", "brick",
]

DOGS = [
    # dog_id, name_fa, emoji, power, hp, defense_chance, income_per_hour, price, currency
    ("stray", "سگ ولگرد", "🐶", 5, 50, 0.10, 20, 500, "tiriak"),
    ("doberman", "دوبرمن", "🐕", 15, 100, 0.25, 60, 3000, "tiriak"),
    ("wolf", "گرگ", "🐺", 30, 180, 0.40, 150, 16000, "tiriak"),
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
        # از REPLACE استفاده می‌کنیم تا اگه weapon_id از قبل با مقادیر قدیمی (مثلا الماس‌محور) وجود داشت،
        # با کاتالوگ جدید بالانس‌شده آپدیت بشه، نه اینکه IGNORE بشه و دست‌نخورده بمونه
        await conn.executemany(
            """INSERT OR REPLACE INTO weapons
               (weapon_id, name_fa, emoji, category, damage, cooldown_sec, price, price_currency,
                required_level, needs_ammo, magazine_size, reload_sec, special_trait, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            WEAPONS,
        )
        # سلاح‌های قدیمی/بی‌ربط (خیار، دمپایی، مشت، پنجه‌بکس و...) دیگه فعال نیستن
        # غیرفعال می‌کنیم نه حذف، چون ممکنه کاربرهای قدیمی توی user_weapons ردیف داشته باشن
        if OLD_WEAPON_IDS_TO_REMOVE:
            placeholders = ",".join("?" for _ in OLD_WEAPON_IDS_TO_REMOVE)
            await conn.execute(
                f"UPDATE weapons SET is_active = 0 WHERE weapon_id IN ({placeholders})",
                OLD_WEAPON_IDS_TO_REMOVE,
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
