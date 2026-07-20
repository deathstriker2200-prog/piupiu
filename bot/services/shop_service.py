from datetime import datetime

from bot.database.repositories import user_repo, weapon_repo


class ShopError(Exception):
    """خطاهای قابل نمایش هنگام خرید"""


async def purchase_weapon(user_id: int, weapon_id: str) -> None:
    weapon = await weapon_repo.get_weapon(weapon_id)
    if weapon is None or not weapon.is_active:
        raise ShopError("سلاح پیدا نشد")

    already_owned = await weapon_repo.user_owns_weapon(user_id, weapon_id)
    if already_owned:
        raise ShopError("already_owned")

    user = await user_repo.get_user(user_id)
    if user is None:
        raise ShopError("کاربر پیدا نشد")

    if user.level < weapon.required_level:
        raise ShopError(f"level_required:{weapon.required_level}")

    if user.tiriak_point < weapon.price:
        raise ShopError("not_enough_money")
    await user_repo.adjust_tiriak(user_id, -weapon.price)

    initial_ammo = weapon.magazine_size if weapon.needs_ammo and weapon.magazine_size else 0
    await weapon_repo.add_weapon_to_user(user_id, weapon_id, initial_ammo)


async def equip_weapon(user_id: int, weapon_id: str) -> None:
    owned = await weapon_repo.user_owns_weapon(user_id, weapon_id)
    if not owned:
        raise ShopError("not_owned")
    await weapon_repo.equip_weapon(user_id, weapon_id)


async def reload_weapon(user_id: int, weapon_id: str) -> None:
    weapon = await weapon_repo.get_weapon(weapon_id)
    if weapon is None or not weapon.needs_ammo:
        raise ShopError("این سلاح نیاز به شارژ نداره")
    await weapon_repo.set_ammo(user_id, weapon_id, weapon.magazine_size or 0)


def ammo_price(weapon) -> int:
    """قیمت یک شارژ کامل مهمات یک سلاح - یک‌سوم قیمت خرید اولیه سلاح"""
    return max(int(weapon.price / 3), 50)


async def purchase_ammo(user_id: int, weapon_id: str) -> int:
    """مهمات یک سلاح رو شارژ می‌کنه و قیمت پرداختی رو برمی‌گردونه"""
    weapon = await weapon_repo.get_weapon(weapon_id)
    if weapon is None or not weapon.is_active:
        raise ShopError("سلاح پیدا نشد")
    if not weapon.needs_ammo:
        raise ShopError("این سلاح نیاز به مهمات نداره")

    owned = await weapon_repo.user_owns_weapon(user_id, weapon_id)
    if not owned:
        raise ShopError("not_owned")

    cooldown_iso = await weapon_repo.get_ammo_cooldown(user_id, weapon_id)
    if cooldown_iso:
        available_dt = datetime.fromisoformat(cooldown_iso)
        if available_dt > datetime.utcnow():
            remaining = int((available_dt - datetime.utcnow()).total_seconds())
            raise ShopError(f"ammo_cooldown:{remaining}")

    user = await user_repo.get_user(user_id)
    if user is None:
        raise ShopError("کاربر پیدا نشد")

    price = ammo_price(weapon)
    if user.tiriak_point < price:
        raise ShopError("not_enough_money")

    await user_repo.adjust_tiriak(user_id, -price)
    await weapon_repo.set_ammo(user_id, weapon_id, weapon.magazine_size or 0)
    return price
