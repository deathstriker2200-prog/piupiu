import random
from datetime import datetime, timedelta

from bot.config.game_config import JAIL_SECONDS, THEFT_SUCCESS_CHANCE
from bot.database.repositories import theft_repo, user_repo


class TheftError(Exception):
    """خطاهای قابل نمایش هنگام تلاش برای دزدی"""


STEAL_PERCENT = 0.15  # درصد تریاک‌پوینت که در صورت موفقیت دزدیده میشه


async def attempt_theft(thief_id: int, target_id: int) -> dict:
    thief = await user_repo.get_user(thief_id)
    target = await user_repo.get_user(target_id)

    if thief is None or target is None:
        raise TheftError("یکی از بازیکن‌ها پیدا نشد")

    if thief.jailed_until:
        jailed_until_dt = datetime.fromisoformat(thief.jailed_until)
        if jailed_until_dt > datetime.utcnow():
            remaining_min = int((jailed_until_dt - datetime.utcnow()).total_seconds() // 60) + 1
            raise TheftError(f"jailed:{remaining_min}")

    if thief.is_dead:
        raise TheftError("thief_dead")

    if target.tiriak_point <= 0:
        raise TheftError("target_no_money")

    success = random.random() < THEFT_SUCCESS_CHANCE

    if success:
        amount = int(target.tiriak_point * STEAL_PERCENT)
        await user_repo.adjust_tiriak(target_id, -amount)
        await user_repo.adjust_tiriak(thief_id, amount)
        await theft_repo.log_theft(thief_id, target_id, True, amount)
        return {"success": True, "amount": amount}
    else:
        jail_until = datetime.utcnow() + timedelta(seconds=JAIL_SECONDS)
        await user_repo.set_jailed_until(thief_id, jail_until.isoformat())
        await theft_repo.log_theft(thief_id, target_id, False, 0)
        return {"success": False, "jail_minutes": JAIL_SECONDS // 60}


async def try_release_if_ready(user_id: int) -> bool:
    """اگه زمان زندان تموم شده باشه آزادش می‌کنه"""
    user = await user_repo.get_user(user_id)
    if user is None or not user.jailed_until:
        return False
    jailed_until_dt = datetime.fromisoformat(user.jailed_until)
    if datetime.utcnow() >= jailed_until_dt:
        await user_repo.set_jailed_until(user_id, None)
        return True
    return False
