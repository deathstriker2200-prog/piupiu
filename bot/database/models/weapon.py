from dataclasses import dataclass
from typing import Optional


@dataclass
class Weapon:
    weapon_id: str
    name_fa: str
    emoji: str
    category: str
    damage: int
    cooldown_sec: int
    price: int
    price_currency: str
    required_level: int
    needs_ammo: bool
    magazine_size: Optional[int]
    reload_sec: Optional[int]
    special_trait: Optional[str]
    is_active: bool

    @classmethod
    def from_row(cls, row) -> "Weapon":
        return cls(
            weapon_id=row["weapon_id"],
            name_fa=row["name_fa"],
            emoji=row["emoji"],
            category=row["category"],
            damage=row["damage"],
            cooldown_sec=row["cooldown_sec"],
            price=row["price"],
            price_currency=row["price_currency"],
            required_level=row["required_level"],
            needs_ammo=bool(row["needs_ammo"]),
            magazine_size=row["magazine_size"],
            reload_sec=row["reload_sec"],
            special_trait=row["special_trait"],
            is_active=bool(row["is_active"]),
        )
