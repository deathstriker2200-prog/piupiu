from bot.config.game_config import (
    DAMAGE_GAIN_PER_LEVEL,
    HP_GAIN_PER_LEVEL,
    STARTING_HP,
    XP_PER_LEVEL_BASE,
    XP_PER_LEVEL_GROWTH,
)
from bot.database.repositories import user_repo


def xp_required_for_level(level: int) -> int:
    """XP لازم برای رسیدن از لول level به level+1"""
    return int(XP_PER_LEVEL_BASE * (XP_PER_LEVEL_GROWTH ** (level - 1)))


def max_hp_for_level(level: int) -> int:
    return STARTING_HP + (level - 1) * HP_GAIN_PER_LEVEL


def bonus_damage_for_level(level: int) -> int:
    return (level - 1) * DAMAGE_GAIN_PER_LEVEL


async def add_xp_and_check_levelup(user_id: int, xp_gain: int) -> list[int]:
    """
    XP اضافه می‌کنه و اگه به لول جدید رسید سطح رو بالا میبره
    برمی‌گردونه لیست لول‌هایی که رد شده (برای نمایش پیام لول‌آپ)
    """
    await user_repo.adjust_xp(user_id, xp_gain)
    user = await user_repo.get_user(user_id)
    if user is None:
        return []

    levels_gained = []
    current_level = user.level
    current_xp = user.xp

    while current_xp >= xp_required_for_level(current_level):
        current_xp -= xp_required_for_level(current_level)
        current_level += 1
        levels_gained.append(current_level)

    if levels_gained:
        new_max_hp = max_hp_for_level(current_level)
        await user_repo.set_level(user_id, current_level, new_max_hp)
        # XP باقیمونده بعد از کسر لول‌های رد شده رو ذخیره کن
        await _set_remaining_xp(user_id, current_xp)

    return levels_gained


async def _set_remaining_xp(user_id: int, remaining_xp: int) -> None:
    user = await user_repo.get_user(user_id)
    if user is None:
        return
    delta = remaining_xp - user.xp
    await user_repo.adjust_xp(user_id, delta)
