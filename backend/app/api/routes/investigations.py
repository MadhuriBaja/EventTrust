
from fastapi import APIRouter, HTTPException, status

from app.models.investigation import (
    InvestigationCreateRequest,
    InvestigationResponse,
)
from app.services.investigation_service import investigation_service
from app.services.research_service import research_service

router = APIRouter(prefix="/investigations", tags=["investigations"])


@router.post(
    "",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an investigation request",
    description=(
        "Accepts an event name and/or event URL and initializes "
        "an investigation request."
    ),
)
def create_investigation(
    request: InvestigationCreateRequest,
) -> InvestigationResponse:
    return investigation_service.create_investigation(request)


@router.get(
    "/{investigation_id}",
    response_model=InvestigationResponse,
    summary="Get investigation details",
    description="Retrieves an investigation request by ID.",
)
def get_investigation(investigation_id: str) -> InvestigationResponse:
    investigation = investigation_service.get_investigation(investigation_id)

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' not found.",
        )

    return investigation


@router.post(
    "/{investigation_id}/research",
    summary="Research an event",
    description=(
        "Searches public sources for event, organizer, venue, "
        "and review information."
    ),
)
def research_investigation(investigation_id: str):
    investigation = investigation_service.get_investigation(investigation_id)

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID '{investigation_id}' not found.",
        )

    event_name = (
        investigation.event_profile.event_name
        if investigation.event_profile
        and investigation.event_profile.event_name
        else investigation.input.event_name
    )

    if not event_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "An event name could not be determined. "
                "Provide an event name or a URL containing event metadata."
            ),
        )

    return research_service.build_report(
        event_name=event_name,
        event_profile=investigation.event_profile,
    )