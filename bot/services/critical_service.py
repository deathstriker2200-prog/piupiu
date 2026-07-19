"""
سیستم Critical واقعی

هر حمله یکی از این نتایج رو می‌گیره:
- Miss: کامل خطا میره، دمیج صفر
- Blocked: حریف تا حدی دفاع کرده، دمیج نصف میشه
- Perfect Block: حریف کامل دفاع کرده، دمیج صفر ولی حریف ضربه نمی‌خوره (نادر)
- Normal: دمیج عادی سلاح
- Critical: دمیج ۱.۵ برابر
- Headshot: دمیج ۲ برابر (نادرتر از Critical)
- Lucky Hit: دمیج ۲.۵ برابر (خیلی نادر، فقط با شانس بالا محتمل‌تره)

ترتیب چک: اول Miss/Block رو رد می‌کنیم، بعد بین نتایج مثبت (Normal/Critical/Headshot/Lucky) قرعه می‌کشیم
"""

import random
from dataclasses import dataclass

from bot.services.luck_service import critical_chance_bonus

BASE_MISS_CHANCE = 0.05
BASE_BLOCK_CHANCE = 0.08
BASE_PERFECT_BLOCK_CHANCE = 0.02

BASE_CRITICAL_CHANCE = 0.12
BASE_HEADSHOT_CHANCE = 0.05
BASE_LUCKY_HIT_CHANCE = 0.015

CRITICAL_MULTIPLIER = 1.5
HEADSHOT_MULTIPLIER = 2.0
LUCKY_HIT_MULTIPLIER = 2.5
BLOCKED_MULTIPLIER = 0.5


@dataclass
class CriticalOutcome:
    result: str          # miss / blocked / perfect_block / normal / critical / headshot / lucky_hit
    damage_multiplier: float
    label_fa: str


def roll_outcome(attacker_luck: int, defender_luck: int = 0) -> CriticalOutcome:
    """
    تاس نتیجه حمله رو می‌ندازه
    attacker_luck رو شانس Critical/Headshot/Lucky بالا می‌بره
    defender_luck (مثلا از سگ نگهبان یا تجهیزات) می‌تونه شانس Block رو بالا ببره - فعلا پایه‌ست
    """
    roll = random.random()

    if roll < BASE_PERFECT_BLOCK_CHANCE:
        return CriticalOutcome("perfect_block", 0.0, "Perfect Block")

    roll -= BASE_PERFECT_BLOCK_CHANCE
    if roll < BASE_BLOCK_CHANCE:
        return CriticalOutcome("blocked", BLOCKED_MULTIPLIER, "Blocked")

    roll -= BASE_BLOCK_CHANCE
    if roll < BASE_MISS_CHANCE:
        return CriticalOutcome("miss", 0.0, "Miss")

    # از اینجا به بعد حمله موفقه، حالا نوعش رو مشخص می‌کنیم
    luck_bonus = critical_chance_bonus(attacker_luck)
    lucky_hit_chance = BASE_LUCKY_HIT_CHANCE + luck_bonus * 0.3
    headshot_chance = BASE_HEADSHOT_CHANCE + luck_bonus * 0.4
    critical_chance = BASE_CRITICAL_CHANCE + luck_bonus * 0.3

    type_roll = random.random()
    if type_roll < lucky_hit_chance:
        return CriticalOutcome("lucky_hit", LUCKY_HIT_MULTIPLIER, "Lucky Hit")

    type_roll -= lucky_hit_chance
    if type_roll < headshot_chance:
        return CriticalOutcome("headshot", HEADSHOT_MULTIPLIER, "Headshot")

    type_roll -= headshot_chance
    if type_roll < critical_chance:
        return CriticalOutcome("critical", CRITICAL_MULTIPLIER, "Critical")

    return CriticalOutcome("normal", 1.0, "")


OUTCOME_EMOJI = {
    "miss": "💨",
    "blocked": "🛡",
    "perfect_block": "🧱",
    "normal": "",
    "critical": "💥",
    "headshot": "🎯",
    "lucky_hit": "🍀",
}
