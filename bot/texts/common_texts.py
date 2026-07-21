def deposit_success(amount: int) -> str:
    return f"💰 {amount} تریاک‌پوینت رفت تو بانک امن شد"


def deposit_fail_capacity() -> str:
    return "ظرفیت بانکت پره برو ارتقاش بده یا کمتر بریز"


def withdraw_success(amount: int) -> str:
    return f"💸 {amount} تریاک‌پوینت از بانک برداشتی"


def withdraw_fail_balance() -> str:
    return "همچین پولی تو بانک نداری بیخیال 😅"


def not_enough_money() -> str:
    return "پول کافی نداری اول یه کاری کن پول جور کنی 💊"


def not_enough_level(required_level: int) -> str:
    return f"لولت کافی نیست باید حداقل لول {required_level} باشی"


def quest_completed(title: str, reward_xp: int, reward_tiriak: int, reward_diamond: int) -> str:
    rewards = []
    if reward_xp:
        rewards.append(f"{reward_xp} ایکس‌پی")
    if reward_tiriak:
        rewards.append(f"{reward_tiriak} تریاک‌پوینت")
    if reward_diamond:
        rewards.append(f"{reward_diamond} الماس")
    reward_str = " و ".join(rewards) if rewards else "یه جایزه کوچیک"
    return f"🎯 کوئست {title} تموم شد گرفتی {reward_str}"


def level_up(new_level: int) -> str:
    return f"🌟 لول رفتی بالا الان لول {new_level} هستی قوی‌تر شدی 💪"


def banned_message() -> str:
    return "شما بن شدید و نمی‌تونید از ربات استفاده کنید 🚫"
