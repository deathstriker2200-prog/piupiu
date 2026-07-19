from dataclasses import dataclass
from typing import Optional


@dataclass
class DogBreed:
    dog_id: str
    name_fa: str
    emoji: str
    power: int
    hp: int
    defense_chance: float
    income_per_hour: int
    price: int
    price_currency: str

    @classmethod
    def from_row(cls, row) -> "DogBreed":
        return cls(
            dog_id=row["dog_id"],
            name_fa=row["name_fa"],
            emoji=row["emoji"],
            power=row["power"],
            hp=row["hp"],
            defense_chance=row["defense_chance"],
            income_per_hour=row["income_per_hour"],
            price=row["price"],
            price_currency=row["price_currency"],
        )


@dataclass
class UserDog:
    id: int
    user_id: int
    dog_id: str
    nickname: Optional[str]
    dog_level: int
    dog_xp: int
    last_fed_at: Optional[str]
    acquired_at: str

    @classmethod
    def from_row(cls, row) -> "UserDog":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            dog_id=row["dog_id"],
            nickname=row["nickname"],
            dog_level=row["dog_level"],
            dog_xp=row["dog_xp"],
            last_fed_at=row["last_fed_at"],
            acquired_at=row["acquired_at"],
        )
