"""Investigation service handling in-memory storage and event extraction."""

from datetime import datetime, timezone
from typing import Dict, Optional
import uuid

from app.models.investigation import (
    InvestigationCreateRequest,
    InvestigationInput,
    InvestigationResponse,
    InvestigationStatus,
)
from app.services.event_extraction_service import event_extraction_service


class InvestigationService:
    """Manages creation and retrieval of investigation requests.

    Uses in-memory storage for the initial foundation layer.
    """

    def __init__(self) -> None:
        self._investigations: Dict[str, InvestigationResponse] = {}

    def create_investigation(
        self,
        request: InvestigationCreateRequest,
    ) -> InvestigationResponse:
        """Creates an investigation and extracts event information when a URL is provided."""

        investigation_id = f"inv_{uuid.uuid4().hex[:12]}"
        created_at = datetime.now(timezone.utc).isoformat()

        investigation_input = InvestigationInput(
            event_name=request.event_name,
            event_url=request.event_url,
        )

        event_profile = None

        if request.event_url:
            event_profile = event_extraction_service.extract_from_url(
                request.event_url
            )

            if not event_profile.event_name and request.event_name:
                event_profile.event_name = request.event_name

        record = InvestigationResponse(
            investigation_id=investigation_id,
            input=investigation_input,
            status=InvestigationStatus.PENDING,
            created_at=created_at,
            event_profile=event_profile,
        )

        self._investigations[investigation_id] = record

        return record

    def get_investigation(
        self,
        investigation_id: str,
    ) -> Optional[InvestigationResponse]:
        """Retrieves an existing investigation by ID."""

        return self._investigations.get(investigation_id)

    def clear(self) -> None:
        """Clears in-memory storage, useful for tests."""

        self._investigations.clear()


# Shared singleton instance
investigation_service = InvestigationService()