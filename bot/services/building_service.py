from datetime import datetime

from bot.database.repositories import building_repo, user_repo

BUILDING_UPGRADE_BASE_COST = 1000


class BuildingError(Exception):
    pass


def _effect_value(base_value: float, growth: float, level: int) -> float:
    return base_value * (growth ** (level - 1)) if level > 0 else 0.0


async def upgrade_building(user_id: int, building_id: str) -> int:
    building_type = await building_repo.get_building_type(building_id)
    if building_type is None:
        raise BuildingError("building_not_found")

    current = await building_repo.get_user_building(user_id, building_id)
    current_level = current["level"] if current else 0
    cost = BUILDING_UPGRADE_BASE_COST * (current_level + 1)

    user = await user_repo.get_user(user_id)
    if user is None or user.tiriak_point < cost:
        raise BuildingError("not_enough_money")

    await user_repo.adjust_tiriak(user_id, -cost)
    new_level = current_level + 1
    await building_repo.upgrade_building(user_id, building_id, new_level)
    return new_level


async def collect_income(user_id: int, building_id: str) -> int:
    """درآمد ساختمان‌های تولیدکننده پول رو جمع می‌کنه (معدن، کارخانه، گلخانه، شرکت)"""
    building = await building_repo.get_user_building(user_id, building_id)
    if building is None or building["level"] <= 0:
        raise BuildingError("not_owned")

    if building["effect_type"] not in ("income", "fixed_income"):
        raise BuildingError("not_income_building")

    now = datetime.utcnow()
    last_collected = building["last_collected_at"]
    if last_collected:
        last_dt = datetime.fromisoformat(last_collected)
        hours_passed = max((now - last_dt).total_seconds() / 3600, 0)
    else:
        hours_passed = 1  # اولین بار یک ساعت حساب کن

    hours_passed = min(hours_passed, 24)  # سقف تجمیع ۲۴ ساعت

    per_hour = _effect_value(building["base_value"], building["value_growth"], building["level"])
    income = int(per_hour * hours_passed)

    await user_repo.adjust_tiriak(user_id, income)
    await building_repo.mark_collected(user_id, building_id, now.isoformat())
    return income
