from dataclasses import dataclass


@dataclass
class Quest:
    quest_id: int
    title: str
    period: str
    goal_type: str
    goal_amount: int
    reward_xp: int
    reward_tiriak: int
    reward_diamond: int
    is_active: bool

    @classmethod
    def from_row(cls, row) -> "Quest":
        return cls(
            quest_id=row["quest_id"],
            title=row["title"],
            period=row["period"],
            goal_type=row["goal_type"],
            goal_amount=row["goal_amount"],
            reward_xp=row["reward_xp"],
            reward_tiriak=row["reward_tiriak"],
            reward_diamond=row["reward_diamond"],
            is_active=bool(row["is_active"]),
        )
