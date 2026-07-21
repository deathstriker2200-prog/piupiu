"""
داده‌های اولیه ثابت بازی (کاتالوگ سلاح‌ها، سگ‌ها، غذا، تجهیزات، ساختمان‌ها)
با اجرای seed_all() این‌ها داخل دیتابیس درج میشن (اگه از قبل نباشن)
این تابع در استارتاپ ربات (یا یک بار دستی) فراخوانی میشه
"""

from bot.database.db import get_conn

WEAPONS = [
    # weapon_id, name_fa, emoji, category, damage(base), cooldown_sec, price, currency,
    # req_level, needs_ammo, mag, reload, special
    # damage پایه طوری تنظیم شده که با ضرب رندوم 0.85-1.15 داخل combat_service دقیقا بازه دمیج درخواستی بشه
    # کولدان همه سلاح‌ها >= کولدان آب‌پاش (15 ثانیه) هست و هرچی سلاح قوی‌تر/گرون‌تر باشه، جایزه هر ثانیه (تریاک‌پوینت/ایکس‌پی) بیشتر میشه
    ("water_gun", "تفنگ آب‌پاش", "💦", "fun", 13, 15, 0, "tiriak", 1, 0, None, None, "سلاح پیش‌فرض رایگان، کمی قوی‌تر شده تا تازه‌کارها ضعیف نباشن"),
    ("knife", "چاقو", "🔪", "melee", 16, 17, 450, "tiriak", 2, 0, None, None, None),
    ("colt", "کلت", "🔫", "firearm", 22, 19, 1500, "tiriak", 4, 0, None, None, None),
    ("shotgun", "شاتگان", "💥", "firearm", 39, 22, 4000, "tiriak", 7, 0, None, None, "دمیج بالا از فاصله نزدیک"),
    ("ak47", "کلاشنیکف", "🪖", "firearm", 55, 20, 8000, "tiriak", 10, 1, 30, 20, None),
    ("m4", "ام۴", "🎯", "firearm", 65, 18, 12000, "tiriak", 13, 1, 30, 18, None),
    ("sniper", "اسنایپر", "🎯", "firearm", 100, 28, 20000, "tiriak", 17, 1, 5, 30, "همیشه کریتیکال"),
    ("rpg", "آرپی‌جی", "💣", "firearm", 180, 35, 35000, "tiriak", 22, 1, 1, 45, "قدرتمندترین سلاح بازی"),
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
    # equipment_id, name_fa, emoji, slot, defense_percent_base(لول 1), defense_percent_growth, required_level
    ("vest", "جلیقه ضدگلوله", "🦺", "vest", 4.0, 1.25, 3),
    ("helmet", "کلاه ایمنی", "⛑", "helmet", 3.0, 1.25, 3),
    ("boots", "چکمه رزمی", "🥾", "boots", 2.0, 1.20, 5),
    ("gloves", "دستکش تاکتیکی", "🧤", "gloves", 2.0, 1.20, 5),
]

BUILDINGS = [
    # building_id, name_fa, emoji, effect_type, base_value(income/hour at level 1), value_growth,
    # required_level(unlock لول ساخت اولیه), is_active, max_level, storage_cap_base(TP), storage_cap_growth
    ("mine", "معدن", "⛏", "income", 200, 1.35, 2, 1, 10, 2000, 1.35),
    ("factory", "کارخانه", "🏭", "income", 350, 1.35, 4, 1, 10, 3200, 1.35),
    ("greenhouse", "گلخانه", "🌿", "income", 550, 1.35, 6, 1, 10, 5000, 1.35),
    ("company", "شرکت", "🏢", "income", 900, 1.35, 8, 1, 10, 8000, 1.35),
]

OLD_BUILDING_IDS_TO_REMOVE = [
    "bank_building", "warehouse", "gang_hq", "military_base",
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
            """INSERT OR REPLACE INTO equipment_catalog
               (equipment_id, name_fa, emoji, slot, defense_percent_base, defense_percent_growth, required_level)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            EQUIPMENT,
        )
        await conn.executemany(
            """INSERT OR REPLACE INTO buildings_catalog
               (building_id, name_fa, emoji, effect_type, base_value, value_growth,
                required_level, is_active, max_level, storage_cap_base, storage_cap_growth)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            BUILDINGS,
        )
        # ساختمان‌های قدیمی که دیگه تو کاتالوگ ۴تایی جدید نیستن رو غیرفعال می‌کنیم
        # (حذف نمی‌کنیم چون ممکنه کاربرهای قدیمی توی user_buildings ردیف داشته باشن و FK بشکنه)
        if OLD_BUILDING_IDS_TO_REMOVE:
            placeholders = ",".join("?" for _ in OLD_BUILDING_IDS_TO_REMOVE)
            await conn.execute(
                f"UPDATE buildings_catalog SET is_active = 0 WHERE building_id IN ({placeholders})",
                OLD_BUILDING_IDS_TO_REMOVE,
            )
        await conn.commit()
