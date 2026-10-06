"""Investigation service handling in-memory storage and lifecycle."""

from datetime import datetime, timezone
from typing import Dict, Optional
import uuid

from app.models.investigation import (
    InvestigationCreateRequest,
    InvestigationInput,
    InvestigationResponse,
    InvestigationStatus,
)


class InvestigationService:
    """Manages creation and retrieval of investigation requests.
    
    Uses in-memory storage for the initial foundation layer.
    """

    def __init__(self) -> None:
        self._investigations: Dict[str, InvestigationResponse] = {}

    def create_investigation(self, request: InvestigationCreateRequest) -> InvestigationResponse:
        """Creates a new investigation request and stores it in memory."""
        investigation_id = f"inv_{uuid.uuid4().hex[:12]}"
        created_at = datetime.now(timezone.utc).isoformat()

        investigation_input = InvestigationInput(
            event_name=request.event_name,
            event_url=request.event_url,
        )

        record = InvestigationResponse(
            investigation_id=investigation_id,
            input=investigation_input,
            status=InvestigationStatus.PENDING,
            created_at=created_at,
        )

        self._investigations[investigation_id] = record
        return record

    def get_investigation(self, investigation_id: str) -> Optional[InvestigationResponse]:
        """Retrieves an existing investigation by ID."""
        return self._investigations.get(investigation_id)

    def clear(self) -> None:
        """Clears in-memory storage, useful for tests."""
        self._investigations.clear()


# Shared singleton instance
investigation_service = InvestigationService()
