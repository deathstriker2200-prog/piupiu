from datetime import datetime, timedelta

from bot.config.game_config import DOG_FEED_COOLDOWN_SECONDS
from bot.database.repositories import dog_repo


class DogError(Exception):
    """خطاهای قابل نمایش هنگام تعامل با سگ"""


# XP لازم برای هر لول سگ (ساده و خطی، قابل تغییر بعدا)
DOG_XP_PER_LEVEL = 100


def dog_level_for_xp(xp: int) -> int:
    return max(1, xp // DOG_XP_PER_LEVEL + 1)


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

    return {
        "xp_gained": food["xp_amount"],
        "leveled_up": leveled_up,
        "new_level": new_level,
    }


async def purchase_dog(user_id: int, dog_id: str) -> None:
    from bot.database.repositories import user_repo

    breed = await dog_repo.get_dog_breed(dog_id)
    if breed is None:
        raise DogError("نژاد سگ پیدا نشد")

    user = await user_repo.get_user(user_id)
    if user is None:
        raise DogError("کاربر پیدا نشد")

    if user.level < breed.required_level:
        raise DogError(f"level_required:{breed.required_level}")

    if breed.price_currency in ("tiriak", "both") and user.tiriak_point < breed.price:
        raise DogError("not_enough_money")
    if breed.price_currency == "diamond" and user.diamond < breed.price:
        raise DogError("not_enough_diamond")

    if breed.price_currency == "diamond":
        await user_repo.adjust_diamond(user_id, -breed.price)
    else:
        await user_repo.adjust_tiriak(user_id, -breed.price)

    await dog_repo.add_dog_to_user(user_id, dog_id)
