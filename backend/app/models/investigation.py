from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.event import EventProfile


class InvestigationStatus(str, Enum):
    PENDING = "pending"


class InvestigationInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_name: Optional[str] = Field(
        default=None,
        description="Name of the event",
    )

    event_url: Optional[str] = Field(
        default=None,
        description="URL or website of the event",
    )


class InvestigationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_name: Optional[str] = Field(
        default=None,
        description="Name of the event to investigate",
    )

    event_url: Optional[str] = Field(
        default=None,
        description="URL of the event to investigate",
    )

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "InvestigationCreateRequest":
        name = (
            self.event_name.strip()
            if self.event_name and self.event_name.strip()
            else None
        )

        url = (
            self.event_url.strip()
            if self.event_url and self.event_url.strip()
            else None
        )

        if not name and not url:
            raise ValueError(
                "Either 'event_name' or 'event_url' must be provided."
            )

        self.event_name = name
        self.event_url = url

        return self


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    investigation_id: str = Field(
        ...,
        description="Unique investigation identifier",
    )

    input: InvestigationInput = Field(
        ...,
        description="Original event input details",
    )

    status: InvestigationStatus = Field(
        ...,
        description="Current status of the investigation",
    )

    created_at: str = Field(
        ...,
        description="ISO 8601 UTC timestamp of creation",
    )

    event_profile: Optional[EventProfile] = Field(
        default=None,
        description="Structured event information discovered during investigation",
    )