"""
دیکشنری مشترک نام فارسی سلاح‌ها به weapon_id
هم برای پارس کردن دستورات متنی خرید (خرید کلاشنیکف / مهمات آرپی‌جی) استفاده میشه
و هم برای هرجایی که لازمه weapon_id به فارسی نشون داده بشه
"""

WEAPON_FA_NAME_TO_ID = {
    "تفنگ آب پاش": "water_gun",
    "تفنگ آب‌پاش": "water_gun",
    "آب پاش": "water_gun",
    "آب‌پاش": "water_gun",
    "چاقو": "knife",
    "کلت": "colt",
    "شاتگان": "shotgun",
    "کلاشنیکف": "ak47",
    "کلاشینکف": "ak47",
    "ام۴": "m4",
    "ام 4": "m4",
    "ام4": "m4",
    "اسنایپر": "sniper",
    "آرپی جی": "rpg",
    "آرپی‌جی": "rpg",
    "ارپی جی": "rpg",
}


def find_weapon_id_by_fa_name(raw_text: str) -> str | None:
    """
    ورودی رو نرمالایز می‌کنه (فاصله‌های اضافه، نیم‌فاصله) و سعی می‌کنه weapon_id متناظرش رو پیدا کنه
    """
    cleaned = raw_text.strip()
    if not cleaned:
        return None

    # تلاش مستقیم
    if cleaned in WEAPON_FA_NAME_TO_ID:
        return WEAPON_FA_NAME_TO_ID[cleaned]

    # نرمالایز کردن نیم‌فاصله و فاصله‌های تکراری
    normalized = " ".join(cleaned.replace("‌", " ").split())
    for name, weapon_id in WEAPON_FA_NAME_TO_ID.items():
        normalized_name = " ".join(name.replace("‌", " ").split())
        if normalized == normalized_name:
            return weapon_id

    # جستجوی زیررشته (مثلا کاربر متن اضافه فرستاده)
    for name, weapon_id in WEAPON_FA_NAME_TO_ID.items():
        normalized_name = " ".join(name.replace("‌", " ").split())
        if normalized_name in normalized or normalized in normalized_name:
            return weapon_id

    return None
