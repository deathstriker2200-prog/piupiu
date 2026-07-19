def team_created(team_name: str) -> str:
    return f"🏴 تیم {team_name} ساخته شد حالا برو بچه جمع کن"


def join_request_sent(team_name: str) -> str:
    return f"درخواستت برای عضویت تو تیم {team_name} رفت واسه لیدر صبر کن جواب بده"


def join_request_received(user_name: str, team_name: str) -> str:
    return f"🔔 {user_name} می‌خواد بیاد تو تیم {team_name} قبول میکنی؟"


def join_accepted(team_name: str) -> str:
    return f"✅ خوش اومدی به تیم {team_name} 🎉"


def join_rejected(team_name: str) -> str:
    return f"❌ درخواستت برای تیم {team_name} رد شد"


def already_in_team() -> str:
    return "تو الان تو یه تیم دیگه‌ای هستی اول باید ازش بری بیرون"


def left_team(team_name: str) -> str:
    return f"از تیم {team_name} اومدی بیرون خداحافظ 👋"
