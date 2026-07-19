"""
سیستم استقامت (Energy)

هر حمله مقداری انرژی مصرف می‌کنه
انرژی به مرور زمان خودش شارژ میشه (یک واحد هر چند دقیقه)
آیتم می‌تونه سقف انرژی رو بالا ببره یا سرعت شارژ رو موقتی افزایش بده
"""

from datetime import datetime, timedelta

from bot.database.db import get_conn

ENERGY_PER_ATTACK = 8
ENERGY_REGEN_PER_TICK = 1
ENERGY_REGEN_TICK_MINUTES = 4  # هر ۴ دقیقه ۱ واحد برمی‌گرده (بدون booster)

BASE_MAX_ENERGY = 100
ENERGY_CAP_UPGRADE_STEP = 20
ENERGY_CAP_UPGRADE_COST = 4000


class EnergyError(Exception):
    pass


async def _get_energy_row(user_id: int) -> dict:
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT energy, max_energy, energy_updated_at FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else {}


async def _apply_regen(user_id: int) -> int:
    """
    قبل از هر استفاده، انرژی رو بر اساس زمان گذشته آپدیت می‌کنه
    برمی‌گردونه مقدار انرژی فعلی بعد از شارژ
    """
    row = await _get_energy_row(user_id)
    if not row:
        return 0

    current_energy = row["energy"]
    max_energy = row["max_energy"]
    last_update = row["energy_updated_at"]

    now = datetime.utcnow()
    if last_update:
        last_dt = datetime.fromisoformat(last_update)
        minutes_passed = (now - last_dt).total_seconds() / 60
        # چک بوستر فعال برای سرعت شارژ بیشتر
        regen_speed_multiplier = await _active_regen_multiplier(user_id)
        effective_tick_minutes = ENERGY_REGEN_TICK_MINUTES / regen_speed_multiplier
        ticks_passed = int(minutes_passed / effective_tick_minutes)
        if ticks_passed > 0:
            gained = ticks_passed * ENERGY_REGEN_PER_TICK
            current_energy = min(max_energy, current_energy + gained)

    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET energy = ?, energy_updated_at = ? WHERE user_id = ?",
            (current_energy, now.isoformat(), user_id),
        )
        await conn.commit()

    return current_energy


async def _active_regen_multiplier(user_id: int) -> float:
    """اگه بوستر شارژ سریع فعال باشه ضریب بیشتر از ۱ برمی‌گردونه"""
    async with get_conn() as conn:
        cursor = await conn.execute(
            "SELECT quantity FROM user_food_inventory WHERE user_id = ? AND food_id = 'energy_booster_active'",
            (user_id,),
        )
        row = await cursor.fetchone()
    # این یه پیاده‌سازی ساده‌ست؛ در آینده میشه با جدول active_effects دقیق‌تر شد
    return 2.0 if row and row["quantity"] > 0 else 1.0


async def get_current_energy(user_id: int) -> tuple[int, int]:
    """انرژی رو شارژ می‌کنه و مقدار فعلی/سقف رو برمی‌گردونه"""
    current = await _apply_regen(user_id)
    row = await _get_energy_row(user_id)
    return current, row.get("max_energy", BASE_MAX_ENERGY)


async def consume_energy(user_id: int, amount: int = ENERGY_PER_ATTACK) -> None:
    """انرژی لازم برای یه حمله رو کم می‌کنه؛ اگه کافی نبود خطا میده"""
    current, max_energy = await get_current_energy(user_id)
    if current < amount:
        raise EnergyError(f"not_enough_energy:{current}:{amount}")

    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET energy = energy - ? WHERE user_id = ?", (amount, user_id)
        )
        await conn.commit()


async def upgrade_energy_cap(user_id: int) -> int:
    """سقف انرژی رو با پرداخت تریاک‌پوینت بالا می‌بره، سقف جدید رو برمی‌گردونه"""
    from bot.database.repositories import user_repo

    user = await user_repo.get_user(user_id)
    if user is None:
        raise EnergyError("user_not_found")

    if user.tiriak_point < ENERGY_CAP_UPGRADE_COST:
        raise EnergyError("not_enough_money")

    await user_repo.adjust_tiriak(user_id, -ENERGY_CAP_UPGRADE_COST)

    async with get_conn() as conn:
        await conn.execute(
            "UPDATE users SET max_energy = max_energy + ? WHERE user_id = ?",
            (ENERGY_CAP_UPGRADE_STEP, user_id),
        )
        await conn.commit()
        cursor = await conn.execute(
            "SELECT max_energy FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row["max_energy"]
