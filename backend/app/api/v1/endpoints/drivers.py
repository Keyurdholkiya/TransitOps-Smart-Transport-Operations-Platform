from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import DatabaseSession, require_roles
from app.models.fleet_enums import DriverStatus
from app.models.role import RoleName
from app.schemas.driver import (
    DriverCreate,
    DriverListResponse,
    DriverResponse,
    DriverStatusUpdate,
    DriverUpdate,
)
from app.services.driver_service import DriverService

router = APIRouter(
    prefix="/drivers",
    tags=["drivers"],
)


@router.post(
    "",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(RoleName.SAFETY_OFFICER))],
)
def create_driver(
    driver_data: DriverCreate,
    session: DatabaseSession,
) -> DriverResponse:
    return DriverService(session).create_driver(driver_data)


@router.get(
    "",
    response_model=DriverListResponse,
    dependencies=[
        Depends(
            require_roles(
                RoleName.SAFETY_OFFICER,
                RoleName.DISPATCHER,
                RoleName.FLEET_MANAGER,
            ),
        ),
    ],
)
def list_drivers(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    driver_status: Annotated[
        DriverStatus | None,
        Query(alias="status"),
    ] = None,
) -> DriverListResponse:
    drivers, total = DriverService(session).list_drivers(
        offset=offset,
        limit=limit,
        driver_status=driver_status,
    )

    return DriverListResponse(
        items=drivers,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{driver_id}",
    response_model=DriverResponse,
    dependencies=[
        Depends(
            require_roles(
                RoleName.SAFETY_OFFICER,
                RoleName.DISPATCHER,
                RoleName.FLEET_MANAGER,
            ),
        ),
    ],
)
def get_driver(
    driver_id: UUID,
    session: DatabaseSession,
) -> DriverResponse:
    return DriverService(session).get_driver(driver_id)


@router.patch(
    "/{driver_id}",
    response_model=DriverResponse,
    dependencies=[Depends(require_roles(RoleName.SAFETY_OFFICER))],
)
def update_driver(
    driver_id: UUID,
    driver_data: DriverUpdate,
    session: DatabaseSession,
) -> DriverResponse:
    return DriverService(session).update_driver(driver_id, driver_data)


@router.patch(
    "/{driver_id}/status",
    response_model=DriverResponse,
    dependencies=[Depends(require_roles(RoleName.SAFETY_OFFICER))],
)
def update_driver_status(
    driver_id: UUID,
    status_data: DriverStatusUpdate,
    session: DatabaseSession,
) -> DriverResponse:
    return DriverService(session).update_status(
        driver_id,
        status_data.status,
    )
