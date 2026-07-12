from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status

from app.models.driver import Driver
from app.models.fleet_enums import DriverStatus, VehicleStatus
from app.models.vehicle import Vehicle


def ensure_vehicle_dispatchable(vehicle: Vehicle) -> None:
    if vehicle.status == VehicleStatus.AVAILABLE:
        return

    status_messages = {
        VehicleStatus.ON_TRIP: "Vehicle is already assigned to a trip.",
        VehicleStatus.IN_SHOP: "Vehicle is currently in the workshop.",
        VehicleStatus.RETIRED: "Retired vehicles cannot be dispatched.",
    }

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=status_messages.get(
            vehicle.status,
            "Vehicle is not available for dispatch.",
        ),
    )


def ensure_driver_dispatchable(
    driver: Driver,
    *,
    current_date: date | None = None,
) -> None:
    effective_date = current_date or date.today()

    if driver.licence_expiry_date < effective_date:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Driver licence has expired.",
        )

    if driver.status == DriverStatus.AVAILABLE:
        return

    status_messages = {
        DriverStatus.ON_TRIP: "Driver is already assigned to a trip.",
        DriverStatus.SUSPENDED: "Suspended drivers cannot be dispatched.",
        DriverStatus.INACTIVE: "Inactive drivers cannot be dispatched.",
    }

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=status_messages.get(
            driver.status,
            "Driver is not available for dispatch.",
        ),
    )


def validate_cargo_capacity(
    vehicle: Vehicle,
    cargo_weight_kg: Decimal,
) -> None:
    if cargo_weight_kg <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cargo weight must be greater than zero.",
        )

    if cargo_weight_kg > vehicle.capacity_kg:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cargo weight exceeds the vehicle capacity.",
        )
