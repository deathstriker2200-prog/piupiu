import random
from datetime import datetime, timedelta

from bot.config.game_config import DOG_FEED_COOLDOWN_SECONDS
from bot.database.repositories import dog_repo

DOG_ATTACK_COOLDOWN_SECONDS = 5 * 60  # کولدان حمله سگ: ۵ دقیقه


class DogError(Exception):
    """خطاهای قابل نمایش هنگام تعامل با سگ"""


# XP لازم برای هر لول سگ (ساده و خطی، قابل تغییر بعدا)
DOG_XP_PER_LEVEL = 100


def dog_level_for_xp(xp: int) -> int:
    return max(1, xp // DOG_XP_PER_LEVEL + 1)


def dog_attack_damage_range(breed_power: int, dog_level: int) -> tuple:
    """
    بازه دمیج حمله سگ بر اساس قدرت نژاد و لول فعلی سگ
    مثلا سگ ولگرد (power=5) لول 1 چیزی حدود 20-30 دمیج میزنه
    و هرچی لولش بره بالاتر این بازه رشد می‌کنه
    """
    base = 20 + (breed_power - 5) * 1.5 + (dog_level - 1) * 4
    min_dmg = max(1, int(base))
    max_dmg = max(min_dmg + 5, int(base * 1.4))
    return min_dmg, max_dmg


async def feed_dog(user_id: int, user_dog_id: int, food_id: str) -> dict:
    dog = await dog_repo.get_user_dog_by_id(user_dog_id)
    if dog is None or dog.user_id != user_id:
        raise DogError("سگ پیدا نشد")

    if dog.last_fed_at:
        last_fed_dt = datetime.fromisoformat(dog.last_fed_at)
        if datetime.utcnow() < last_fed_dt + timedelta(seconds=DOG_FEED_COOLDOWN_SECONDS):
            raise DogError("dog_full")

    food = await dog_repo.get_food(food_id)
    if food is None:
        raise DogError("غذا پیدا نشد")

    has_food = await dog_repo.consume_food(user_id, food_id)
    if not has_food:
        raise DogError("no_food_in_inventory")

    now_iso = datetime.utcnow().isoformat()
    await dog_repo.feed_dog(user_dog_id, food["xp_amount"], now_iso)

    updated_dog = await dog_repo.get_user_dog_by_id(user_dog_id)
    old_level = dog.dog_level
    new_level = dog_level_for_xp(updated_dog.dog_xp)
    leveled_up = new_level > old_level
    if leveled_up:
        await dog_repo.set_dog_level(user_dog_id, new_level)
        breed = await dog_repo.get_dog_breed(dog.dog_id)
        if breed:
            dmg_min, dmg_max = dog_attack_damage_range(breed.power, new_level)
            await dog_repo.set_dog_attack_damage(user_dog_id, dmg_min, dmg_max)

    return {
        "xp_gained": food["xp_amount"],
        "leveled_up": leveled_up,
        "new_level": new_level,
    }


async def purchase_dog(user_id: int, dog_id: str, nickname: str) -> int:
    from bot.database.repositories import user_repo

    breed = await dog_repo.get_dog_breed(dog_id)
    if breed is None:
        raise DogError("نژاد سگ پیدا نشد")

    nickname = nickname.strip()
    if not nickname or len(nickname) > 20:
        raise DogError("invalid_name")

    existing = await dog_repo.get_user_dog_by_nickname(user_id, nickname)
    if existing:
        raise DogError("name_taken")

    user = await user_repo.get_user(user_id)
    if user is None:
        raise DogError("کاربر پیدا نشد")

    if user.level < breed.required_level:
        raise DogError(f"level_required:{breed.required_level}")

    if user.tiriak_point < breed.price:
        raise DogError("not_enough_money")

    await user_repo.adjust_tiriak(user_id, -breed.price)

    user_dog_id = await dog_repo.add_dog_to_user(user_id, dog_id, nickname)
    dmg_min, dmg_max = dog_attack_damage_range(breed.power, 1)
    await dog_repo.set_dog_attack_damage(user_dog_id, dmg_min, dmg_max)
    return user_dog_id


async def find_user_dog_by_name(user_id: int, dog_name: str):
    return await dog_repo.get_user_dog_by_nickname(user_id, dog_name.strip())


async def attack_with_dog(owner_id: int, user_dog_id: int, target_user_id: int) -> dict:
    """سگ رو برای حمله به یه بازیکن هدف می‌فرسته"""
    from bot.database.repositories import user_repo as user_repo_module

    dog = await dog_repo.get_user_dog_by_id(user_dog_id)
    if dog is None or dog.user_id != owner_id:
        raise DogError("سگ پیدا نشد")

    if dog.attack_cooldown_until:
        cooldown_dt = datetime.fromisoformat(dog.attack_cooldown_until)
        if datetime.utcnow() < cooldown_dt:
            seconds_left = max(0, int((cooldown_dt - datetime.utcnow()).total_seconds()))
            raise DogError(f"cooldown:{seconds_left}")

    target = await user_repo_module.get_user(target_user_id)
    if target is None:
        raise DogError("هدف پیدا نشد")
    if target.is_dead:
        raise DogError("target_dead")

    damage = random.randint(dog.attack_damage_min, dog.attack_damage_max)
    new_hp = max(0, target.hp - damage)
    target_died = new_hp <= 0 and damage > 0

    if target_died:
        from bot.services.combat_service import _handle_death

        await _handle_death(target_user_id, owner_id, 0)
    else:
        await user_repo_module.update_hp(target_user_id, new_hp)

    cooldown_until = datetime.utcnow() + timedelta(seconds=DOG_ATTACK_COOLDOWN_SECONDS)
    await dog_repo.set_dog_attack_cooldown(user_dog_id, cooldown_until.isoformat())

    return {
        "damage": damage,
        "target_remaining_hp": new_hp,
        "target_max_hp": target.max_hp,
        "target_died": target_died,
    }
