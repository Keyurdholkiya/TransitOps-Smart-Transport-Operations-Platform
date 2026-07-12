from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import DatabaseSession, require_roles
from app.models.fleet_enums import VehicleStatus, VehicleType
from app.models.role import RoleName
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
    VehicleStatusUpdate,
    VehicleUpdate,
)
from app.services.vehicle_service import VehicleService

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
)


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(RoleName.FLEET_MANAGER))],
)
def create_vehicle(
    vehicle_data: VehicleCreate,
    session: DatabaseSession,
) -> VehicleResponse:
    return VehicleService(session).create_vehicle(vehicle_data)


@router.get(
    "",
    response_model=VehicleListResponse,
    dependencies=[
        Depends(
            require_roles(
                RoleName.FLEET_MANAGER,
                RoleName.DISPATCHER,
            ),
        ),
    ],
)
def list_vehicles(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    vehicle_status: Annotated[
        VehicleStatus | None,
        Query(alias="status"),
    ] = None,
    vehicle_type: Annotated[
        VehicleType | None,
        Query(),
    ] = None,
) -> VehicleListResponse:
    vehicles, total = VehicleService(session).list_vehicles(
        offset=offset,
        limit=limit,
        vehicle_status=vehicle_status,
        vehicle_type=vehicle_type,
    )

    return VehicleListResponse(
        items=vehicles,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    dependencies=[
        Depends(
            require_roles(
                RoleName.FLEET_MANAGER,
                RoleName.DISPATCHER,
            ),
        ),
    ],
)
def get_vehicle(
    vehicle_id: UUID,
    session: DatabaseSession,
) -> VehicleResponse:
    return VehicleService(session).get_vehicle(vehicle_id)


@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    dependencies=[Depends(require_roles(RoleName.FLEET_MANAGER))],
)
def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    session: DatabaseSession,
) -> VehicleResponse:
    return VehicleService(session).update_vehicle(vehicle_id, vehicle_data)


@router.patch(
    "/{vehicle_id}/status",
    response_model=VehicleResponse,
    dependencies=[Depends(require_roles(RoleName.FLEET_MANAGER))],
)
def update_vehicle_status(
    vehicle_id: UUID,
    status_data: VehicleStatusUpdate,
    session: DatabaseSession,
) -> VehicleResponse:
    return VehicleService(session).update_status(
        vehicle_id,
        status_data.status,
    )
