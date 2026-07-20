import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from bot.config.game_config import (
    AMMO_REPURCHASE_COOLDOWN_SECONDS,
    DEATH_RESPAWN_SECONDS,
    DEFAULT_WEAPON_ID,
    KILL_TIRIAK_BONUS,
)
from bot.database.repositories import user_repo, weapon_repo
from bot.services import combo_service
from bot.services.attack_line_service import get_varied_attack_line
from bot.services.critical_service import CriticalOutcome, roll_outcome
from bot.services.energy_service import EnergyError, consume_energy
from bot.services.level_service import add_xp_and_check_levelup, bonus_damage_for_level


class CombatError(Exception):
    """خطاهای قابل نمایش به کاربر حین حمله (کولدان، مرده بودن، تیر تموم، انرژی کم و غیره)"""


@dataclass
class AttackResult:
    weapon_name: str
    weapon_emoji: str
    weapon_id: str
    damage: int
    target_max_hp: int
    target_remaining_hp: int
    tiriak_stolen: int
    target_died: bool
    # فیلدهای نسخه ۲
    outcome: str              # miss/blocked/perfect_block/normal/critical/headshot/lucky_hit
    outcome_label: str
    combo_count: int
    combo_damage_bonus_applied: bool
    flavor_text: str
    # جایزه‌های شلیک
    tiriak_reward: int         # جایزه معمولی شلیک (بدون احتساب کیل‌بونس و سرقت)
    xp_reward: int
    kill_bonus_tiriak: int     # فقط اگه target_died باشه پر میشه (KILL_TIRIAK_BONUS)
    total_tiriak_reward: int   # مجموع همه جایزه‌های تریاک‌پوینت این شلیک برای مهاجم
    ran_out_of_ammo: bool      # همین شلیک آخرین تیر رو مصرف کرد
    respawn_minutes: int       # فقط اگه target_died باشه معتبره


STEAL_PERCENT_ON_KILL = 0.05  # درصد تریاک‌پوینت که هنگام کشتن از قربانی دزدیده میشه
KILL_XP_BASE = 80  # پایه XP کشتن، به علاوه قدرت سلاح


async def resolve_attack(attacker_id: int, target_id: int) -> AttackResult:
    attacker = await user_repo.get_user(attacker_id)
    target = await user_repo.get_user(target_id)

    if attacker is None or target is None:
        raise CombatError("یکی از بازیکن‌ها پیدا نشد")

    if attacker.is_dead:
        raise CombatError("attacker_dead")

    if attacker.jailed_until:
        jailed_until_dt = datetime.fromisoformat(attacker.jailed_until)
        if jailed_until_dt > datetime.utcnow():
            raise CombatError("attacker_jailed")

    if target.is_dead:
        seconds_left = 0
        if target.died_at:
            died_at_dt = datetime.fromisoformat(target.died_at)
            respawn_dt = died_at_dt + timedelta(seconds=DEATH_RESPAWN_SECONDS)
            seconds_left = max(0, int((respawn_dt - datetime.utcnow()).total_seconds()))
        raise CombatError(f"target_dead:{seconds_left}")

    weapon_row = await weapon_repo.get_equipped_weapon(attacker_id)
    if weapon_row is None:
        raise CombatError("no_weapon")

    weapon_id = weapon_row["weapon_id"]

    # چک کولدان
    cooldown_at = await weapon_repo.get_cooldown(attacker_id, weapon_id)
    if cooldown_at:
        available_dt = datetime.fromisoformat(cooldown_at)
        if available_dt > datetime.utcnow():
            remaining = int((available_dt - datetime.utcnow()).total_seconds())
            raise CombatError(f"cooldown:{remaining}")

    # چک انرژی
    try:
        await consume_energy(attacker_id)
    except EnergyError as e:
        raise CombatError(str(e))

    # چک تیر برای سلاح‌های گرم
    ran_out_of_ammo = False
    if weapon_row["needs_ammo"]:
        if weapon_row["ammo_current"] <= 0:
            raise CombatError(f"out_of_ammo:{weapon_row['name_fa']}")
        remaining_ammo = weapon_row["ammo_current"] - 1
        await weapon_repo.set_ammo(attacker_id, weapon_id, remaining_ammo)
        if remaining_ammo <= 0:
            ran_out_of_ammo = True
            # سلاح فعال به‌صورت خودکار به تفنگ آب‌پاش تغییر می‌کنه
            await weapon_repo.equip_weapon(attacker_id, DEFAULT_WEAPON_ID)
            # یک دقیقه کول‌دان برای خرید دوباره مهمات همین سلاح
            ammo_cooldown_until = datetime.utcnow() + timedelta(seconds=AMMO_REPURCHASE_COOLDOWN_SECONDS)
            await weapon_repo.set_ammo_cooldown(attacker_id, weapon_id, ammo_cooldown_until.isoformat())

    # نتیجه Critical رو مشخص کن (Miss/Block/Normal/Critical/Headshot/Lucky Hit)
    outcome: CriticalOutcome = roll_outcome(attacker.luck)

    base_damage = weapon_row["damage"] + bonus_damage_for_level(attacker.level)
    randomized = base_damage * random.uniform(0.85, 1.15)
    damage = max(0, int(randomized * outcome.damage_multiplier))

    was_successful_hit = outcome.result not in ("miss", "perfect_block")
    combo_count = await combo_service.register_hit(attacker_id, was_successful_hit)

    combo_bonus_applied = False
    combo_tier = combo_service.combo_tier_for_count(combo_count)
    if combo_tier and damage > 0:
        _, dmg_mult, _ = combo_tier
        damage = int(damage * dmg_mult)
        combo_bonus_applied = True

    if outcome.result == "perfect_block":
        damage = 0

    new_hp = target.hp - damage
    target_died = damage > 0 and new_hp <= 0

    # جایزه هر شلیک: بر اساس قدرت سلاح و دمیج واقعی وارد شده
    tiriak_reward = 0
    xp_reward = 0
    if damage > 0:
        tiriak_reward = int(damage * 2 + weapon_row["damage"] * 0.5)
        xp_reward = int(damage * 0.3 + weapon_row["damage"] * 0.15)

    tiriak_stolen = 0
    kill_bonus_tiriak = 0
    respawn_minutes = 0
    if target_died:
        tiriak_stolen = int(target.tiriak_point * STEAL_PERCENT_ON_KILL)
        await _handle_death(target_id, attacker_id, tiriak_stolen)
        await user_repo.increment_kills(attacker_id)

        kill_bonus_tiriak = KILL_TIRIAK_BONUS
        xp_reward += KILL_XP_BASE + weapon_row["damage"]
        respawn_minutes = max(1, DEATH_RESPAWN_SECONDS // 60)
    elif damage > 0:
        await user_repo.update_hp(target_id, new_hp)

    total_tiriak_reward = tiriak_reward + kill_bonus_tiriak
    if total_tiriak_reward > 0:
        await user_repo.adjust_tiriak(attacker_id, total_tiriak_reward)
    if xp_reward > 0:
        await add_xp_and_check_levelup(attacker_id, xp_reward)

    # ست کردن کولدان بعدی
    cooldown_until = datetime.utcnow() + timedelta(seconds=weapon_row["cooldown_sec"])
    await weapon_repo.set_cooldown(attacker_id, weapon_id, cooldown_until.isoformat())

    await weapon_repo.log_attack(
        attacker_id, target_id, weapon_id, damage, tiriak_stolen, target_died
    )

    attacker_name = attacker.full_name or attacker.username or "بازیکن"
    target_name = target.full_name or target.username or "بازیکن"
    flavor_text = await get_varied_attack_line(
        attacker_id, weapon_id, attacker_name, target_name, damage
    )

    return AttackResult(
        weapon_name=weapon_row["name_fa"],
        weapon_emoji=weapon_row["emoji"],
        weapon_id=weapon_id,
        damage=damage,
        target_max_hp=target.max_hp,
        target_remaining_hp=max(new_hp, 0) if damage > 0 else target.hp,
        tiriak_stolen=tiriak_stolen,
        target_died=target_died,
        outcome=outcome.result,
        outcome_label=outcome.label_fa,
        combo_count=combo_count,
        combo_damage_bonus_applied=combo_bonus_applied,
        flavor_text=flavor_text,
        tiriak_reward=tiriak_reward,
        xp_reward=xp_reward,
        kill_bonus_tiriak=kill_bonus_tiriak,
        total_tiriak_reward=total_tiriak_reward,
        ran_out_of_ammo=ran_out_of_ammo,
        respawn_minutes=respawn_minutes,
    )


async def _handle_death(target_id: int, killer_id: int, tiriak_stolen: int) -> None:
    """مدیریت مرگ بازیکن - چک بانک برای تصمیم از دست دادن ۵۰٪ پول یا نه"""
    from bot.database.repositories import bank_repo

    bank = await bank_repo.get_bank(target_id)
    bank_balance = bank["balance"] if bank else 0

    if bank_balance <= 0:
        target = await user_repo.get_user(target_id)
        if target:
            loss = int(target.tiriak_point * 0.5)
            await user_repo.adjust_tiriak(target_id, -loss)

    if tiriak_stolen > 0:
        await user_repo.adjust_tiriak(target_id, -tiriak_stolen)
        await user_repo.adjust_tiriak(killer_id, tiriak_stolen)

    await user_repo.set_dead(target_id, datetime.utcnow().isoformat())


async def try_respawn_if_ready(user_id: int) -> bool:
    """اگه زمان respawn رسیده باشه بازیکن رو زنده می‌کنه، برمی‌گردونه آیا زنده شد یا نه"""
    user = await user_repo.get_user(user_id)
    if user is None or not user.is_dead or not user.died_at:
        return False
    died_at_dt = datetime.fromisoformat(user.died_at)
    if datetime.utcnow() >= died_at_dt + timedelta(seconds=DEATH_RESPAWN_SECONDS):
        await user_repo.respawn(user_id)
        return True
    return False
