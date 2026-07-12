from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models.driver import Driver
from app.models.fleet_enums import DriverStatus, VehicleStatus, VehicleType
from app.models.vehicle import Vehicle
from app.schemas.driver import DriverCreate
from app.schemas.vehicle import VehicleCreate
from app.services.fleet_rules import (
    ensure_driver_dispatchable,
    ensure_vehicle_dispatchable,
    validate_cargo_capacity,
)


def build_vehicle(
    *,
    status: VehicleStatus = VehicleStatus.AVAILABLE,
    capacity_kg: Decimal = Decimal("10000.00"),
) -> Vehicle:
    return Vehicle(
        registration_number="GJ01AB1234",
        vehicle_type=VehicleType.TRUCK,
        manufacturer="Tata",
        model="Prima",
        manufacturing_year=2025,
        capacity_kg=capacity_kg,
        odometer_km=Decimal("1000.00"),
        status=status,
    )


def build_driver(
    *,
    status: DriverStatus = DriverStatus.AVAILABLE,
    licence_expiry_date: date | None = None,
) -> Driver:
    return Driver(
        employee_code="DRV001",
        full_name="Test Driver",
        email="driver@example.com",
        phone_number="+919876543210",
        licence_number="GJ0120250000123",
        licence_category="Heavy Vehicle",
        licence_expiry_date=licence_expiry_date or date.today() + timedelta(days=365),
        joining_date=date.today() - timedelta(days=365),
        status=status,
    )


def test_vehicle_schema_normalizes_registration_number() -> None:
    vehicle = VehicleCreate(
        registration_number=" gj 01 ab 1234 ",
        vehicle_type=VehicleType.TRUCK,
        manufacturer=" Tata ",
        model=" Prima ",
        manufacturing_year=2025,
        capacity_kg=Decimal("12000.00"),
    )

    assert vehicle.registration_number == "GJ01AB1234"
    assert vehicle.manufacturer == "Tata"
    assert vehicle.model == "Prima"


def test_driver_schema_normalizes_identifiers_and_email() -> None:
    driver = DriverCreate(
        employee_code=" drv 001 ",
        full_name=" Test Driver ",
        email=" DRIVER@EXAMPLE.COM ",
        phone_number="+91 9876543210",
        licence_number=" gj 01 20250000123 ",
        licence_category=" Heavy Vehicle ",
        licence_expiry_date=date.today() + timedelta(days=365),
        joining_date=date.today(),
    )

    assert driver.employee_code == "DRV001"
    assert driver.email == "driver@example.com"
    assert driver.phone_number == "+919876543210"
    assert driver.licence_number == "GJ0120250000123"


def test_available_vehicle_can_be_dispatched() -> None:
    vehicle = build_vehicle()

    ensure_vehicle_dispatchable(vehicle)


@pytest.mark.parametrize(
    "vehicle_status",
    [
        VehicleStatus.ON_TRIP,
        VehicleStatus.IN_SHOP,
        VehicleStatus.RETIRED,
    ],
)
def test_unavailable_vehicle_cannot_be_dispatched(
    vehicle_status: VehicleStatus,
) -> None:
    vehicle = build_vehicle(status=vehicle_status)

    with pytest.raises(HTTPException) as exception:
        ensure_vehicle_dispatchable(vehicle)

    assert exception.value.status_code == 409


def test_available_driver_with_valid_licence_can_be_dispatched() -> None:
    driver = build_driver()

    ensure_driver_dispatchable(driver)


@pytest.mark.parametrize(
    "driver_status",
    [
        DriverStatus.ON_TRIP,
        DriverStatus.SUSPENDED,
        DriverStatus.INACTIVE,
    ],
)
def test_unavailable_driver_cannot_be_dispatched(
    driver_status: DriverStatus,
) -> None:
    driver = build_driver(status=driver_status)

    with pytest.raises(HTTPException) as exception:
        ensure_driver_dispatchable(driver)

    assert exception.value.status_code == 409


def test_driver_with_expired_licence_cannot_be_dispatched() -> None:
    driver = build_driver(
        licence_expiry_date=date.today() - timedelta(days=1),
    )

    with pytest.raises(HTTPException) as exception:
        ensure_driver_dispatchable(driver)

    assert exception.value.status_code == 409
    assert exception.value.detail == "Driver licence has expired."


def test_cargo_within_vehicle_capacity_is_allowed() -> None:
    vehicle = build_vehicle(capacity_kg=Decimal("10000.00"))

    validate_cargo_capacity(vehicle, Decimal("8000.00"))


def test_cargo_above_vehicle_capacity_is_rejected() -> None:
    vehicle = build_vehicle(capacity_kg=Decimal("10000.00"))

    with pytest.raises(HTTPException) as exception:
        validate_cargo_capacity(vehicle, Decimal("12000.00"))

    assert exception.value.status_code == 409


def test_non_positive_cargo_weight_is_rejected() -> None:
    vehicle = build_vehicle()

    with pytest.raises(HTTPException) as exception:
        validate_cargo_capacity(vehicle, Decimal("0.00"))

    assert exception.value.status_code == 422
