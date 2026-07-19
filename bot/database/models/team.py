from dataclasses import dataclass
from typing import Optional


@dataclass
class Team:
    team_id: int
    name: str
    logo_emoji: Optional[str]
    description: Optional[str]
    capacity: int
    owner_id: int
    created_at: str

    @classmethod
    def from_row(cls, row) -> "Team":
        return cls(
            team_id=row["team_id"],
            name=row["name"],
            logo_emoji=row["logo_emoji"],
            description=row["description"],
            capacity=row["capacity"],
            owner_id=row["owner_id"],
            created_at=row["created_at"],
        )
