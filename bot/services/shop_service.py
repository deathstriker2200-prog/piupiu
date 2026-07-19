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

    if weapon.price_currency == "diamond":
        if user.diamond < weapon.price:
            raise ShopError("not_enough_diamond")
        await user_repo.adjust_diamond(user_id, -weapon.price)
    elif weapon.price_currency == "both":
        if user.tiriak_point < weapon.price or user.diamond < 1:
            raise ShopError("not_enough_money")
        await user_repo.adjust_tiriak(user_id, -weapon.price)
    else:  # tiriak
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
