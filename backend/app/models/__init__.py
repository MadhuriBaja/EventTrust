"""Data models package."""

from app.models.investigation import (
    InvestigationCreateRequest,
    InvestigationInput,
    InvestigationResponse,
    InvestigationStatus,
)

__all__ = [
    "InvestigationCreateRequest",
    "InvestigationInput",
    "InvestigationResponse",
    "InvestigationStatus",
]
