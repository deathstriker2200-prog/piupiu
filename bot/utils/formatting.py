def hp_bar(current: int, maximum: int, length: int = 10) -> str:
    current = max(current, 0)
    filled = int((current / maximum) * length) if maximum > 0 else 0
    filled = min(filled, length)
    return "🟩" * filled + "⬛" * (length - filled)


def format_seconds(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} ثانیه"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} دقیقه"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes:
        return f"{hours} ساعت و {remaining_minutes} دقیقه"
    return f"{hours} ساعت"


def format_currency(amount: int) -> str:
    return f"{amount:,}".replace(",", "٬")
