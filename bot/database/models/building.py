from dataclasses import dataclass


@dataclass
class BuildingType:
    building_id: str
    name_fa: str
    emoji: str
    effect_type: str
    base_value: float
    value_growth: float
    required_level: int
    is_active: bool
    max_level: int
    storage_cap_base: float
    storage_cap_growth: float

    @classmethod
    def from_row(cls, row) -> "BuildingType":
        keys = row.keys()
        return cls(
            building_id=row["building_id"],
            name_fa=row["name_fa"],
            emoji=row["emoji"],
            effect_type=row["effect_type"],
            base_value=row["base_value"],
            value_growth=row["value_growth"],
            required_level=row["required_level"] if "required_level" in keys else 1,
            is_active=bool(row["is_active"]) if "is_active" in keys else True,
            max_level=row["max_level"] if "max_level" in keys else 10,
            storage_cap_base=row["storage_cap_base"] if "storage_cap_base" in keys else 2000,
            storage_cap_growth=row["storage_cap_growth"] if "storage_cap_growth" in keys else 1.3,
        )
