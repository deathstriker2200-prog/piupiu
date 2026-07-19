from dataclasses import dataclass


@dataclass
class BuildingType:
    building_id: str
    name_fa: str
    emoji: str
    effect_type: str
    base_value: float
    value_growth: float

    @classmethod
    def from_row(cls, row) -> "BuildingType":
        return cls(
            building_id=row["building_id"],
            name_fa=row["name_fa"],
            emoji=row["emoji"],
            effect_type=row["effect_type"],
            base_value=row["base_value"],
            value_growth=row["value_growth"],
        )
