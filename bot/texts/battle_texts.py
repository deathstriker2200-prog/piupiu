"""
متن‌های مربوط به نبرد
تم طنز و خودمونی - بدون نقطه آخر جمله - ویرگول کم
"""

WELCOME_GROUP = (
    "سلام رفقا بنگ بنگ اومد وسط 💊🔫\n"
    "همه با ۱۰۰ HP شروع می‌کنید برید بترکونید 😎"
)


def attack_result(
    attacker_name: str,
    target_name: str,
    weapon_emoji: str,
    weapon_name: str,
    damage: int,
    remaining_hp: int,
    stolen: int,
) -> str:
    lines = [
        f"{weapon_emoji} {attacker_name} با {weapon_name} زد تو پر {target_name} 💥",
        f"Damage {damage} خورد",
        f"HP باقی مونده {target_name} {max(remaining_hp, 0)}",
    ]
    if stolen > 0:
        lines.append(f"{stolen} تریاک‌پوینت هم دزدید 💊")
    return "\n".join(lines)


OUTCOME_LABELS_FA = {
    "miss": "💨 خطا رفت",
    "blocked": "🛡 تا حدی دفاع شد",
    "perfect_block": "🧱 دفاع کامل، هیچ دمیجی نخورد",
    "critical": "💥 Critical",
    "headshot": "🎯 Headshot",
    "lucky_hit": "🍀 Lucky Hit",
}


def attack_result_v2(
    flavor_text: str,
    outcome: str,
    damage: int,
    remaining_hp: int,
    stolen: int,
    combo_count: int,
    combo_bonus_applied: bool,
) -> str:
    """نسخه کامل‌تر نمایش نتیجه حمله با Critical و Combo"""
    lines = [flavor_text]

    special_label = OUTCOME_LABELS_FA.get(outcome)
    if special_label:
        lines.append(special_label)

    if outcome not in ("miss", "perfect_block"):
        lines.append(f"Damage {damage}")
        lines.append(f"HP باقی مونده حریف {max(remaining_hp, 0)}")
        if stolen > 0:
            lines.append(f"{stolen} تریاک‌پوینت هم دزدید 💊")

    if combo_bonus_applied:
        lines.append(f"🔥 Combo ×{combo_count} فعاله دمیج اضافه گرفتی")
    elif combo_count >= 2:
        lines.append(f"Combo ×{combo_count}")

    return "\n".join(lines)


def not_enough_energy(current: int, needed: int) -> str:
    return f"🔋 انرژیت کافی نیست ({current}/{needed}) کمی صبر کن شارژ بشه یا بوستر بزن"


def target_died(target_name: str) -> str:
    return (
        f"💀 {target_name} داغون شد و رفت زیر خاک\n"
        "۵ دقیقه دیگه دوباره زنده میشه صبر کن 😴"
    )


def death_lost_money(amount: int) -> str:
    return f"چون پول تو بانک نداشتی {amount} تریاک‌پوینت از دستت رفت 😢"


def death_bank_safe() -> str:
    return "خوبه پولت تو بانک بود چیزی از دست ندادی 😌"


def cooldown_active(seconds_left: int) -> str:
    return f"⏳ صبر کن هنوز کولدانت تموم نشده {seconds_left} ثانیه دیگه بزن"


def target_is_dead_already(target_name: str) -> str:
    return f"{target_name} الان مرده نمیشه بهش شلیک کرد 😂"


def attacker_is_dead() -> str:
    return "تو الان مردی نمیتونی حمله کنی صبر کن respawn شی 💀"


def attacker_is_jailed(minutes_left: int) -> str:
    return f"👮🏽‍♂️ تو زندانی هنوز {minutes_left} دقیقه مونده صبر کن"


def no_weapon_equipped() -> str:
    return "سلاحی تجهیز نکردی برو تو پیوی یه سلاح انتخاب کن 🔫"


def out_of_ammo(weapon_name: str) -> str:
    return f"تیر {weapon_name} تموم شده برو Reload کن یا تیر بخر 🔄"


def respawned(user_name: str) -> str:
    return f"🌟 {user_name} دوباره زنده شد بزن بریم"
