"""
متن‌های مربوط به نبرد
تم طنز و خودمونی - بدون نقطه آخر جمله - ویرگول کم
"""

WELCOME_GROUP = (
    "سلام رفقا بنگ بنگ اومد وسط 💊🔫\n"
    "همه با ۲۰۰ HP شروع می‌کنید برید بترکونید 😎"
)


def _weapon_emoji_for_text(weapon_emoji: str) -> str:
    """ایموجی سرخط پیام شلیک، بر اساس ایموجی خود سلاح یکی از این چند حالت رو برمی‌گردونه"""
    if weapon_emoji == "💣":
        return "💣"
    if weapon_emoji == "💥":
        return "💥"
    if weapon_emoji == "💦":
        return "💦"
    if weapon_emoji == "🔪":
        return "🔪"
    return "🔫"


def attack_result_alive(
    weapon_name: str,
    weapon_emoji: str,
    target_name: str,
    damage: int,
    tiriak_reward: int,
    xp_reward: int,
    remaining_hp: int,
    max_hp: int,
) -> str:
    """پیام شلیک وقتی هدف زنده می‌ماند"""
    header_emoji = _weapon_emoji_for_text(weapon_emoji)
    return (
        f"{header_emoji} با «{weapon_name}» به {target_name} شلیک کردی و {damage} دمیج زدی!\n\n"
        f"💰 +{tiriak_reward} تریاک‌پوینت\n"
        f"⭐ +{xp_reward} XP\n\n"
        f"❤️ سلامتی باقی‌مانده {target_name}:\n"
        f"{max(remaining_hp, 0)} / {max_hp}"
    )


def attack_result_killed(
    weapon_name: str,
    weapon_emoji: str,
    target_name: str,
    damage: int,
    kill_bonus: int,
    total_tiriak_reward: int,
    xp_reward: int,
    respawn_minutes: int,
) -> str:
    """پیام شلیک وقتی هدف کشته می‌شود"""
    header_emoji = _weapon_emoji_for_text(weapon_emoji) if weapon_emoji != "🔫" else "💥"
    return (
        f"{header_emoji} با «{weapon_name}» به {target_name} شلیک کردی و {damage} دمیج زدی!\n\n"
        f"☠️ {target_name} مُرد و {kill_bonus} تریاک‌پوینت از جایزه کشتن دریافت کردی.\n\n"
        f"💰 +{total_tiriak_reward} تریاک‌پوینت\n"
        f"⭐ +{xp_reward} XP\n\n"
        f"⏳ {target_name} تا {respawn_minutes} دقیقه دیگر مرده می‌ماند و سپس با سلامتی کامل زنده می‌شود."
    )


def ammo_depleted(weapon_name: str) -> str:
    """پیام اتمام مهمات - وقتی همون شلیک آخرین تیر رو مصرف کرده"""
    return (
        f"⚠️ مهمات «{weapon_name}» تمام شد.\n\n"
        "🔫 سلاح فعال به «تفنگ آب‌پاش» تغییر کرد.\n\n"
        "🕐 یک دقیقه دیگر می‌توانی دوباره برای این سلاح مهمات بخری."
    )


OUTCOME_LABELS_FA = {
    "miss": "💨 خطا رفت",
    "blocked": "🛡 تا حدی دفاع شد",
    "perfect_block": "🧱 دفاع کامل، هیچ دمیجی نخورد",
    "critical": "💥 Critical",
    "headshot": "🎯 Headshot",
    "lucky_hit": "🍀 Lucky Hit",
}


def not_enough_energy(current: int, needed: int) -> str:
    return f"🔋 انرژیت کافی نیست ({current}/{needed}) کمی صبر کن شارژ بشه یا بوستر بزن"


def death_lost_money(amount: int) -> str:
    return f"چون پول تو بانک نداشتی {amount} تریاک‌پوینت از دستت رفت 😢"


def death_bank_safe() -> str:
    return "خوبه پولت تو بانک بود چیزی از دست ندادی 😌"


def cooldown_active(seconds_left: int) -> str:
    return f"⏳ صبر کن هنوز کولدانت تموم نشده {seconds_left} ثانیه دیگه بزن"


def target_is_dead_already(target_name: str, minutes_left: int) -> str:
    return (
        f"☠️ {target_name} همین الان مرده است.\n\n"
        f"⏳ تا {minutes_left} دقیقه دیگر زنده نمی‌شود.\n\n"
        "🚫 فعلاً نمی‌توانی به او شلیک کنی."
    )


def attacker_is_dead() -> str:
    return "تو الان مردی نمیتونی حمله کنی صبر کن respawn شی 💀"


def attacker_is_jailed(minutes_left: int) -> str:
    return f"👮🏽‍♂️ تو زندانی هنوز {minutes_left} دقیقه مونده صبر کن"


def no_weapon_equipped() -> str:
    return "سلاحی تجهیز نکردی برو تو پیوی یه سلاح انتخاب کن 🔫"


def out_of_ammo(weapon_name: str) -> str:
    return f"تیر «{weapon_name}» تموم شده، یه دقیقه صبر کن یا بعدش مهماتشو بخر 🔄"


def self_shoot_attempt() -> str:
    return "😅 عزیز دل به خود...\n\nنمی‌تونی به خودت شلیک کنی!"


def bot_shoot_attempt() -> str:
    return "😅 رو من که نمیشه شلیک کرد، من فقط این وسط رفری می‌کنم نه اینکه HP داشته باشم 😎"


def respawned(user_name: str) -> str:
    return f"🌟 {user_name} دوباره زنده شد بزن بریم"
