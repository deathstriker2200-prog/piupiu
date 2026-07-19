def dog_full_already() -> str:
    return "داداش این دیگه ترکید از بس خورد 😂"


def dog_fed(dog_name: str, xp_gained: int) -> str:
    return f"🐶 {dog_name} خورد و خوشحال شد +{xp_gained} XP گرفت"


def dog_leveled_up(dog_name: str, new_level: int) -> str:
    return f"🎉 {dog_name} رفت لول {new_level} قوی‌تر شد"


def dog_purchased(dog_name: str) -> str:
    return f"🐕 مبارک باشه {dog_name} رو خریدی مراقبش باش"
