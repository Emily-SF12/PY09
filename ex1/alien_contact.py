from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def check_contact_rules(self) -> "AlienContact":
        if not self.contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC' "
                             "(Alien Contact)")
        if (self.contact_type == ContactType.PHYSICAL
                and not self.is_verified):
            raise ValueError("Physical contact reports must be verified")
        if (self.contact_type == ContactType.TELEPATHIC
                and self.witness_count < 3):
            raise ValueError("Telepathic contact requires "
                             "at least 3 witnesses")
        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError("Strong signals (> 7.0) should include "
                             "received messages")
        return self


def show_contact(contact: AlienContact) -> None:
    print("Valid contact report:")
    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    if contact.message_received is not None:
        print(f"Message: '{contact.message_received}'")


def show_errors(error: ValidationError) -> None:
    print("Expected validation error:")
    for detail in error.errors():
        print(detail["msg"].removeprefix("Value error, "))


def try_invalid(title: str, data: dict[str, Any]) -> None:
    print()
    print("=" * 38)
    print(f"[{title}]")
    try:
        AlienContact.model_validate(data)
        print("No error raised, the report should have been rejected!")
    except ValidationError as e:
        show_errors(e)


def main() -> None:
    print("Alien Contact Log Validation")
    print("=" * 38)
    valid_data: dict[str, Any] = {
        "contact_id": "AC_2024_001",
        "timestamp": "2024-07-02T23:45:00",
        "location": "Area 51, Nevada",
        "contact_type": "radio",
        "signal_strength": 8.5,
        "duration_minutes": 45,
        "witness_count": 5,
        "message_received": "Greetings from Zeta Reticuli",
    }
    try:
        show_contact(AlienContact.model_validate(valid_data))
    except ValidationError as e:
        print(f"Unexpected validation error: {e}")
    try_invalid("Telepathic contact with 2 witnesses", dict(
        valid_data, contact_type="telepathic", witness_count=2))
    try_invalid("Contact ID without the AC prefix", dict(
        valid_data, contact_id="XX_2024_002"))
    try_invalid("Unverified physical contact", dict(
        valid_data, contact_type="physical"))
    try_invalid("Strong signal without a message", dict(
        valid_data, message_received=None))
    try_invalid("Unknown contact type", dict(
        valid_data, contact_type="dream"))


if __name__ == "__main__":
    main()
