from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def check_mission_safety(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")
        leaders: list[CrewMember] = [
            member for member in self.crew
            if member.rank in (Rank.COMMANDER, Rank.CAPTAIN)
        ]
        if len(leaders) == 0:
            raise ValueError("Mission must have at least one "
                             "Commander or Captain")
        if self.duration_days > 365:
            veterans: list[CrewMember] = [
                member for member in self.crew
                if member.years_experience >= 5
            ]
            if len(veterans) * 2 < len(self.crew):
                raise ValueError("Long missions (> 365 days) need at least "
                                 "50% experienced crew (5+ years)")
        for member in self.crew:
            if not member.is_active:
                raise ValueError("All crew members must be active "
                                 f"({member.name} is inactive)")
        return self


def show_mission(mission: SpaceMission) -> None:
    print("Valid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(f"- {member.name} ({member.rank.value}) "
              f"- {member.specialization}")


def show_errors(error: ValidationError) -> None:
    print("Expected validation error:")
    for detail in error.errors():
        message: str = detail["msg"].removeprefix("Value error, ")
        location: str = ".".join(str(part) for part in detail["loc"])
        if location == "":
            print(message)
        else:
            print(f"{location}: {message}")


def try_invalid(title: str, data: dict[str, Any]) -> None:
    print()
    print("=" * 41)
    print(f"[{title}]")
    try:
        SpaceMission.model_validate(data)
        print("No error raised, the mission should have been rejected!")
    except ValidationError as e:
        show_errors(e)


def build_crew() -> list[dict[str, Any]]:
    return [
        {"member_id": "CM001", "name": "Sarah Connor", "rank": "commander",
         "age": 45, "specialization": "Mission Command",
         "years_experience": 20},
        {"member_id": "CM002", "name": "John Smith", "rank": "lieutenant",
         "age": 36, "specialization": "Navigation",
         "years_experience": 8},
        {"member_id": "CM003", "name": "Alice Johnson", "rank": "officer",
         "age": 29, "specialization": "Engineering",
         "years_experience": 3},
    ]


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 41)
    valid_data: dict[str, Any] = {
        "mission_id": "M2024_MARS",
        "mission_name": "Mars Colony Establishment",
        "destination": "Mars",
        "launch_date": "2024-09-15T08:00:00",
        "duration_days": 900,
        "crew": build_crew(),
        "budget_millions": 2500.0,
    }
    try:
        show_mission(SpaceMission.model_validate(valid_data))
    except ValidationError as e:
        print(f"Unexpected validation error: {e}")
    no_leader: list[dict[str, Any]] = build_crew()
    no_leader[0]["rank"] = "lieutenant"
    try_invalid("Crew without Commander or Captain",
                dict(valid_data, crew=no_leader))
    rookies: list[dict[str, Any]] = build_crew()
    rookies[1]["years_experience"] = 2
    try_invalid("Long mission with rookie crew",
                dict(valid_data, crew=rookies))
    inactive: list[dict[str, Any]] = build_crew()
    inactive[2]["is_active"] = False
    try_invalid("Inactive crew member", dict(valid_data, crew=inactive))
    try_invalid("Mission ID without the M prefix",
                dict(valid_data, mission_id="X2024_MARS"))
    too_young: list[dict[str, Any]] = build_crew()
    too_young[2]["age"] = 15
    try_invalid("Nested crew member fails its own validation",
                dict(valid_data, crew=too_young))


if __name__ == "__main__":
    main()
