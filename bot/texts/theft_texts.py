THEFT_WARNING = "⚠️ در صورت عدم موفقیت در دزدی راهی گونی خواهی شد 👮🏽‍♂️"


def theft_success(thief_name: str, target_name: str, amount: int) -> str:
    return f"🥷 {thief_name} با موفقیت {amount} تریاک‌پوینت از {target_name} دزدید 💊"


def theft_fail(thief_name: str, jail_minutes: int) -> str:
    return f"👮🏽‍♂️ {thief_name} گیر افتاد و رفت زندان برای {jail_minutes} دقیقه 🚔"


def already_jailed(minutes_left: int) -> str:
    return f"تو الان زندانی هستی {minutes_left} دقیقه دیگه مونده صبر کن 🔒"


def target_has_no_money() -> str:
    return "این بدبخت اصلا پولی نداره که بدزدی 😂"
