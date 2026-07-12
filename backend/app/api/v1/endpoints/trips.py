from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import DatabaseSession, require_roles
from app.models.role import RoleName
from app.models.trip_enums import TripStatus, TripType
from app.schemas.trip import (
    TripCancellationRequest,
    TripCompletionRequest,
    TripCreate,
    TripListResponse,
    TripResponse,
)
from app.services.trip_service import TripService

router = APIRouter(
    prefix="/trips",
    tags=["trips"],
)


@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(RoleName.DISPATCHER))],
)
def create_trip(
    trip_data: TripCreate,
    session: DatabaseSession,
) -> TripResponse:
    return TripService(session).create_trip(trip_data)


@router.get(
    "",
    response_model=TripListResponse,
    dependencies=[
        Depends(
            require_roles(
                RoleName.DISPATCHER,
                RoleName.FLEET_MANAGER,
            ),
        ),
    ],
)
def list_trips(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    trip_status: Annotated[
        TripStatus | None,
        Query(alias="status"),
    ] = None,
    trip_type: Annotated[
        TripType | None,
        Query(),
    ] = None,
    vehicle_id: Annotated[
        UUID | None,
        Query(),
    ] = None,
    driver_id: Annotated[
        UUID | None,
        Query(),
    ] = None,
) -> TripListResponse:
    trips, total = TripService(session).list_trips(
        offset=offset,
        limit=limit,
        trip_status=trip_status,
        trip_type=trip_type,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
    )

    return TripListResponse(
        items=trips,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{trip_id}",
    response_model=TripResponse,
    dependencies=[
        Depends(
            require_roles(
                RoleName.DISPATCHER,
                RoleName.FLEET_MANAGER,
            ),
        ),
    ],
)
def get_trip(
    trip_id: UUID,
    session: DatabaseSession,
) -> TripResponse:
    return TripService(session).get_trip(trip_id)


@router.post(
    "/{trip_id}/dispatch",
    response_model=TripResponse,
    dependencies=[Depends(require_roles(RoleName.DISPATCHER))],
)
def dispatch_trip(
    trip_id: UUID,
    session: DatabaseSession,
) -> TripResponse:
    return TripService(session).dispatch_trip(trip_id)


@router.post(
    "/{trip_id}/complete",
    response_model=TripResponse,
    dependencies=[Depends(require_roles(RoleName.DISPATCHER))],
)
def complete_trip(
    trip_id: UUID,
    completion_data: TripCompletionRequest,
    session: DatabaseSession,
) -> TripResponse:
    return TripService(session).complete_trip(
        trip_id,
        completion_data,
    )


@router.post(
    "/{trip_id}/cancel",
    response_model=TripResponse,
    dependencies=[Depends(require_roles(RoleName.DISPATCHER))],
)
def cancel_trip(
    trip_id: UUID,
    cancellation_data: TripCancellationRequest,
    session: DatabaseSession,
) -> TripResponse:
    return TripService(session).cancel_trip(
        trip_id,
        cancellation_data,
    )
