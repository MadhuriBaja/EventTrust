from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EventProfile(BaseModel):
    """
    Structured information about an event discovered during an investigation.

    These fields are populated from the event page and later cross-checked
    using external evidence sources such as Google Search, News, Maps, and YouTube.
    """

    model_config = ConfigDict(extra="ignore")

    event_name: Optional[str] = Field(
        default=None,
        description="Name of the event",
    )

    organizer: Optional[str] = Field(
        default=None,
        description="Organizer or organizing organization",
    )

    event_date: Optional[str] = Field(
        default=None,
        description="Event date or date range",
    )

    venue: Optional[str] = Field(
        default=None,
        description="Event venue or location",
    )

    speakers: List[str] = Field(
        default_factory=list,
        description="Speakers, guests, or important people listed for the event",
    )

    registration_url: Optional[str] = Field(
        default=None,
        description="Registration or ticket/payment URL",
    )

    source_url: Optional[str] = Field(
        default=None,
        description="Original event page used as the starting source",
    )

    description: Optional[str] = Field(
        default=None,
        description="Event description extracted from the source page",
    )