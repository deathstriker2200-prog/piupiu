import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from bot.config.game_config import DEATH_RESPAWN_SECONDS
from bot.database.repositories import user_repo, weapon_repo
from bot.services import combo_service
from bot.services.attack_line_service import get_varied_attack_line
from bot.services.critical_service import CriticalOutcome, roll_outcome
from bot.services.energy_service import EnergyError, consume_energy
from bot.services.level_service import bonus_damage_for_level


class CombatError(Exception):
    """خطاهای قابل نمایش به کاربر حین حمله (کولدان، مرده بودن، تیر تموم، انرژی کم و غیره)"""


@dataclass
class AttackResult:
    weapon_name: str
    weapon_emoji: str
    damage: int
    target_remaining_hp: int
    tiriak_stolen: int
    target_died: bool
    # فیلدهای نسخه ۲
    outcome: str              # miss/blocked/perfect_block/normal/critical/headshot/lucky_hit
    outcome_label: str
    combo_count: int
    combo_damage_bonus_applied: bool
    flavor_text: str


STEAL_PERCENT_ON_KILL = 0.05  # درصد تریاک‌پوینت که هنگام کشتن از قربانی دزدیده میشه


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
        raise CombatError("target_dead")

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
    if weapon_row["needs_ammo"]:
        if weapon_row["ammo_current"] <= 0:
            raise CombatError(f"out_of_ammo:{weapon_row['name_fa']}")
        await weapon_repo.set_ammo(attacker_id, weapon_id, weapon_row["ammo_current"] - 1)

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

    tiriak_stolen = 0
    if target_died:
        tiriak_stolen = int(target.tiriak_point * STEAL_PERCENT_ON_KILL)
        await _handle_death(target_id, attacker_id, tiriak_stolen)
        await user_repo.increment_kills(attacker_id)
    elif damage > 0:
        await user_repo.update_hp(target_id, new_hp)

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
        damage=damage,
        target_remaining_hp=max(new_hp, 0) if damage > 0 else target.hp,
        tiriak_stolen=tiriak_stolen,
        target_died=target_died,
        outcome=outcome.result,
        outcome_label=outcome.label_fa,
        combo_count=combo_count,
        combo_damage_bonus_applied=combo_bonus_applied,
        flavor_text=flavor_text,
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
