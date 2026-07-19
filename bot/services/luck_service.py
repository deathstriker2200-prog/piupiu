"""
سیستم شانس (Luck)

Luck یه عدد بین ۰ تا ۱۰۰ هست که رو خیلی جاها تاثیر می‌ذاره
این ماژول یه‌جا نگه‌داری می‌کنه که Luck چطور روی هر مکانیزم اثر بذاره
تا همه‌جای پروژه یکدست باشه و بالانس بازی دستکاری نشه
"""

MAX_LUCK = 100


def luck_factor(luck: int) -> float:
    """Luck رو به یه ضریب بین ۰ تا ۱ تبدیل می‌کنه"""
    return min(max(luck, 0), MAX_LUCK) / MAX_LUCK


def critical_chance_bonus(luck: int) -> float:
    """Luck چقدر به شانس Critical اضافه می‌کنه (حداکثر ۱۵٪ اضافه)"""
    return luck_factor(luck) * 0.15


def item_find_chance_bonus(luck: int) -> float:
    """Luck چقدر به شانس پیدا کردن آیتم تصادفی اضافه می‌کنه (حداکثر ۲۰٪)"""
    return luck_factor(luck) * 0.20


def quest_reward_multiplier(luck: int) -> float:
    """Luck چقدر جایزه کوئست رو ضرب می‌کنه (بین ۱.۰ تا ۱.۳)"""
    return 1.0 + luck_factor(luck) * 0.30


def drop_chance_bonus(luck: int) -> float:
    """Luck چقدر به شانس Drop دشمن بعد کشتن اضافه می‌کنه (حداکثر ۲۵٪)"""
    return luck_factor(luck) * 0.25


def event_trigger_bonus(luck: int) -> float:
    """Luck چقدر شانس گیر افتادن تو یه Mini Event خوب رو بالا می‌بره (حداکثر ۱۰٪)"""
    return luck_factor(luck) * 0.10


def diamond_find_chance_bonus(luck: int) -> float:
    """Luck چقدر به شانس پیدا کردن الماس اضافه می‌کنه (حداکثر ۱۲٪)"""
    return luck_factor(luck) * 0.12
