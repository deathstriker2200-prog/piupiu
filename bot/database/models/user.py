from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id: int
    username: Optional[str]
    full_name: Optional[str]
    hp: int
    max_hp: int
    level: int
    xp: int
    tiriak_point: int
    diamond: int
    kills: int
    is_dead: bool
    died_at: Optional[str]
    jailed_until: Optional[str]
    is_banned: bool
    created_at: str
    last_active_at: str
    # v2 fields
    energy: int
    max_energy: int
    energy_updated_at: Optional[str]
    luck: int
    combo_count: int
    combo_updated_at: Optional[str]
    reputation: int
    login_streak: int
    last_login_at: Optional[str]
    streak_freeze_available: int
    last_active_group_id: Optional[int]

    @classmethod
    def from_row(cls, row) -> "User":
        keys = row.keys()
        return cls(
            user_id=row["user_id"],
            username=row["username"],
            full_name=row["full_name"],
            hp=row["hp"],
            max_hp=row["max_hp"],
            level=row["level"],
            xp=row["xp"],
            tiriak_point=row["tiriak_point"],
            diamond=row["diamond"],
            kills=row["kills"],
            is_dead=bool(row["is_dead"]),
            died_at=row["died_at"],
            jailed_until=row["jailed_until"],
            is_banned=bool(row["is_banned"]),
            created_at=row["created_at"],
            last_active_at=row["last_active_at"],
            energy=row["energy"] if "energy" in keys else 100,
            max_energy=row["max_energy"] if "max_energy" in keys else 100,
            energy_updated_at=row["energy_updated_at"] if "energy_updated_at" in keys else None,
            luck=row["luck"] if "luck" in keys else 10,
            combo_count=row["combo_count"] if "combo_count" in keys else 0,
            combo_updated_at=row["combo_updated_at"] if "combo_updated_at" in keys else None,
            reputation=row["reputation"] if "reputation" in keys else 0,
            login_streak=row["login_streak"] if "login_streak" in keys else 0,
            last_login_at=row["last_login_at"] if "last_login_at" in keys else None,
            streak_freeze_available=row["streak_freeze_available"] if "streak_freeze_available" in keys else 0,
            last_active_group_id=row["last_active_group_id"] if "last_active_group_id" in keys else None,
        )
