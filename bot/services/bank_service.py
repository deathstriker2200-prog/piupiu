from bot.config.game_config import BANK_UPGRADE_CAPACITY_STEP
from bot.database.repositories import bank_repo, user_repo


class BankError(Exception):
    pass


async def deposit(user_id: int, amount: int) -> None:
    if amount <= 0:
        raise BankError("invalid_amount")
    user = await user_repo.get_user(user_id)
    if user is None or user.tiriak_point < amount:
        raise BankError("not_enough_money")
    ok = await bank_repo.deposit(user_id, amount)
    if not ok:
        raise BankError("capacity_full")


async def withdraw(user_id: int, amount: int) -> None:
    if amount <= 0:
        raise BankError("invalid_amount")
    ok = await bank_repo.withdraw(user_id, amount)
    if not ok:
        raise BankError("not_enough_balance")


UPGRADE_COST_PER_LEVEL = 2000


async def upgrade_bank(user_id: int) -> int:
    """ارتقای ظرفیت بانک، برمی‌گردونه ظرفیت جدید"""
    bank = await bank_repo.get_bank(user_id)
    if bank is None:
        raise BankError("no_bank_account")

    cost = UPGRADE_COST_PER_LEVEL * bank["level"]
    user = await user_repo.get_user(user_id)
    if user is None or user.tiriak_point < cost:
        raise BankError("not_enough_money")

    await user_repo.adjust_tiriak(user_id, -cost)
    new_capacity = bank["capacity"] + BANK_UPGRADE_CAPACITY_STEP
    new_level = bank["level"] + 1
    await bank_repo.upgrade_capacity(user_id, new_capacity, new_level)
    return new_capacity
