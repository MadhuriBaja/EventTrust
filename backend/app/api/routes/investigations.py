from fastapi import APIRouter, HTTPException, status

from app.models.investigation import (
    InvestigationCreateRequest,
    InvestigationResponse,
)
from app.services.investigation_service import investigation_service

router = APIRouter(prefix="/investigations", tags=["investigations"])


@router.post(
    "",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an investigation request",
    description="Accepts an event name and/or event URL and initializes an investigation request.",
)
def create_investigation(request: InvestigationCreateRequest) -> InvestigationResponse:
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
