from datetime import datetime

from bot.database.repositories import building_repo, user_repo

BUILDING_UPGRADE_BASE_COST = 1000
BUILDING_UPGRADE_COST_GROWTH = 1.6

# هر ۵ لول بازیکن، سقف لول ساختمان یکی زیاد میشه
# لول بازیکن ۵ → سقف لول ساختمان ۲، لول ۱۰ → سقف ۳، لول ۱۵ → سقف ۴ و به همین ترتیب
PLAYER_LEVELS_PER_BUILDING_LEVEL = 5


class BuildingError(Exception):
    pass


def _effect_value(base_value: float, growth: float, level: int) -> float:
    return base_value * (growth ** (level - 1)) if level > 0 else 0.0


def building_level_cap_for_player_level(player_level: int) -> int:
    """حداکثر لولی که یک ساختمان می‌تونه بر اساس لول فعلی بازیکن داشته باشه"""
    return 1 + (player_level // PLAYER_LEVELS_PER_BUILDING_LEVEL)


def upgrade_cost(current_level: int) -> int:
    """هزینه ساخت (لول ۰ به ۱) یا ارتقا به لول بعدی"""
    return int(BUILDING_UPGRADE_BASE_COST * (BUILDING_UPGRADE_COST_GROWTH ** current_level))


def storage_cap_for_level(building_type, level: int) -> float:
    if level <= 0:
        return 0.0
    return building_type.storage_cap_base * (building_type.storage_cap_growth ** (level - 1))


def income_per_hour_for_level(building_type, level: int) -> float:
    return _effect_value(building_type.base_value, building_type.value_growth, level)


async def upgrade_building(user_id: int, building_id: str) -> int:
    building_type = await building_repo.get_building_type(building_id)
    if building_type is None or not building_type.is_active:
        raise BuildingError("building_not_found")

    current = await building_repo.get_user_building(user_id, building_id)
    current_level = current["level"] if current else 0

    user = await user_repo.get_user(user_id)
    if user is None:
        raise BuildingError("user_not_found")

    if current_level == 0 and user.level < building_type.required_level:
        raise BuildingError(f"level_required:{building_type.required_level}")

    level_cap = building_level_cap_for_player_level(user.level)
    if current_level >= building_type.max_level:
        raise BuildingError("max_level_reached")
    if current_level >= level_cap:
        # حداقل لول بازیکن لازم برای این لول بعدی ساختمان
        needed_player_level = (current_level) * PLAYER_LEVELS_PER_BUILDING_LEVEL
        raise BuildingError(f"player_level_cap:{needed_player_level}")

    cost = upgrade_cost(current_level)
    if user.tiriak_point < cost:
        raise BuildingError("not_enough_money")

    await user_repo.adjust_tiriak(user_id, -cost)
    new_level = current_level + 1
    await building_repo.upgrade_building(user_id, building_id, new_level)
    return new_level


async def collect_income(user_id: int, building_id: str) -> int:
    """درآمد جمع‌شده (بر اساس سقف ذخیره‌سازی ساختمان) رو برداشت می‌کنه"""
    building_type = await building_repo.get_building_type(building_id)
    building = await building_repo.get_user_building(user_id, building_id)
    if building is None or building["level"] <= 0 or building_type is None:
        raise BuildingError("not_owned")

    accumulated = int(building.get("accumulated_income", 0) or 0)
    if accumulated <= 0:
        raise BuildingError("nothing_to_collect")

    await user_repo.adjust_tiriak(user_id, accumulated)
    await building_repo.reset_accumulated_income(user_id, building_id, datetime.utcnow().isoformat())
    return accumulated


async def get_building_progress(user_id: int, building_id: str) -> dict:
    """
    مقدار درآمد جمع‌شده فعلی رو با توجه به زمان گذشته از آخرین محاسبه به‌روز می‌کنه
    (بدون برداشت کردنش) و اطلاعات کامل نمایش رو برمی‌گردونه
    """
    building_type = await building_repo.get_building_type(building_id)
    building = await building_repo.get_user_building(user_id, building_id)
    level = building["level"] if building else 0

    per_hour = income_per_hour_for_level(building_type, level) if level > 0 else 0
    cap = storage_cap_for_level(building_type, level) if level > 0 else 0

    accumulated = float(building.get("accumulated_income", 0) or 0) if building else 0.0
    last_calc = building.get("last_collected_at") if building else None

    if level > 0 and last_calc:
        last_dt = datetime.fromisoformat(last_calc)
        hours_passed = max((datetime.utcnow() - last_dt).total_seconds() / 3600, 0)
        accumulated = min(cap, accumulated + per_hour * hours_passed)
        await building_repo.set_accumulated_income(
            user_id, building_id, accumulated, datetime.utcnow().isoformat()
        )
    elif level > 0 and not last_calc:
        await building_repo.set_accumulated_income(user_id, building_id, 0, datetime.utcnow().isoformat())

    return {
        "level": level,
        "per_hour": per_hour,
        "cap": cap,
        "accumulated": int(accumulated),
    }
