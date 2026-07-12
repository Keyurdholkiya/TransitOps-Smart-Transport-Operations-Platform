from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.fleet_enums import (
    DriverStatus,
    VehicleStatus,
    VehicleType,
)
from app.models.trip import Trip
from app.models.trip_enums import TripStatus, TripType
from app.models.vehicle import Vehicle
from app.schemas.trip import (
    TripCancellationRequest,
    TripCompletionRequest,
    TripCreate,
)
from app.services.trip_service import TripService


def create_trip_records(
    session: Session,
    *,
    trip_status: TripStatus = TripStatus.PLANNED,
) -> tuple[Trip, Vehicle, Driver]:
    resource_status = (
        VehicleStatus.ON_TRIP
        if trip_status == TripStatus.IN_PROGRESS
        else VehicleStatus.AVAILABLE
    )
    driver_status = (
        DriverStatus.ON_TRIP
        if trip_status == TripStatus.IN_PROGRESS
        else DriverStatus.AVAILABLE
    )

    vehicle = Vehicle(
        registration_number="GJ01TR1234",
        vehicle_type=VehicleType.TRUCK,
        manufacturer="Tata",
        model="Prima",
        manufacturing_year=2025,
        capacity_kg=Decimal("10000.00"),
        odometer_km=Decimal("5000.00"),
        status=resource_status,
    )
    driver = Driver(
        employee_code="TRIPDRV001",
        full_name="Trip Test Driver",
        email="trip-driver@example.com",
        phone_number="+919876543210",
        licence_number="GJTRIP2026001",
        licence_category="Heavy Vehicle",
        licence_expiry_date=date.today() + timedelta(days=365),
        joining_date=date.today() - timedelta(days=365),
        status=driver_status,
    )

    session.add_all([vehicle, driver])
    session.flush()

    trip = Trip(
        trip_number="TRIP-TEST-001",
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        trip_type=TripType.DELIVERY,
        origin="Ahmedabad",
        destination="Surat",
        cargo_weight_kg=Decimal("5000.00"),
        status=trip_status,
    )

    session.add(trip)
    session.flush()

    return trip, vehicle, driver


def test_trip_schema_normalizes_trip_number_and_locations() -> None:
    trip_data = TripCreate(
        trip_number=" trip 001 ",
        vehicle_id="00000000-0000-0000-0000-000000000001",
        driver_id="00000000-0000-0000-0000-000000000002",
        trip_type=TripType.DELIVERY,
        origin=" Ahmedabad ",
        destination=" Surat ",
        cargo_weight_kg=Decimal("1000.00"),
    )

    assert trip_data.trip_number == "TRIP001"
    assert trip_data.origin == "Ahmedabad"
    assert trip_data.destination == "Surat"


def test_dispatch_updates_trip_vehicle_and_driver(
    db_session: Session,
) -> None:
    trip, vehicle, driver = create_trip_records(db_session)

    dispatched_trip = TripService(db_session).dispatch_trip(trip.id)

    assert dispatched_trip.status == TripStatus.IN_PROGRESS
    assert dispatched_trip.dispatched_at is not None
    assert vehicle.status == VehicleStatus.ON_TRIP
    assert driver.status == DriverStatus.ON_TRIP


def test_trip_cannot_be_dispatched_twice(
    db_session: Session,
) -> None:
    trip, _, _ = create_trip_records(db_session)
    service = TripService(db_session)

    service.dispatch_trip(trip.id)

    with pytest.raises(HTTPException) as exception:
        service.dispatch_trip(trip.id)

    assert exception.value.status_code == 409
    assert exception.value.detail == ("Only a planned trip can be dispatched.")


def test_completion_restores_resources_and_updates_odometer(
    db_session: Session,
) -> None:
    trip, vehicle, driver = create_trip_records(
        db_session,
        trip_status=TripStatus.IN_PROGRESS,
    )

    completed_trip = TripService(db_session).complete_trip(
        trip.id,
        TripCompletionRequest(
            final_odometer_km=Decimal("5250.50"),
        ),
    )

    assert completed_trip.status == TripStatus.COMPLETED
    assert completed_trip.completed_at is not None
    assert completed_trip.final_odometer_km == Decimal("5250.50")
    assert vehicle.status == VehicleStatus.AVAILABLE
    assert vehicle.odometer_km == Decimal("5250.50")
    assert driver.status == DriverStatus.AVAILABLE


def test_completion_rejects_lower_odometer(
    db_session: Session,
) -> None:
    trip, vehicle, driver = create_trip_records(
        db_session,
        trip_status=TripStatus.IN_PROGRESS,
    )

    with pytest.raises(HTTPException) as exception:
        TripService(db_session).complete_trip(
            trip.id,
            TripCompletionRequest(
                final_odometer_km=Decimal("4999.00"),
            ),
        )

    assert exception.value.status_code == 409
    assert trip.status == TripStatus.IN_PROGRESS
    assert vehicle.status == VehicleStatus.ON_TRIP
    assert driver.status == DriverStatus.ON_TRIP


def test_planned_trip_cancellation_does_not_change_resources(
    db_session: Session,
) -> None:
    trip, vehicle, driver = create_trip_records(db_session)

    cancelled_trip = TripService(db_session).cancel_trip(
        trip.id,
        TripCancellationRequest(
            reason="Customer cancelled the delivery.",
        ),
    )

    assert cancelled_trip.status == TripStatus.CANCELLED
    assert cancelled_trip.cancelled_at is not None
    assert cancelled_trip.cancellation_reason == ("Customer cancelled the delivery.")
    assert vehicle.status == VehicleStatus.AVAILABLE
    assert driver.status == DriverStatus.AVAILABLE


def test_active_trip_cancellation_restores_resources(
    db_session: Session,
) -> None:
    trip, vehicle, driver = create_trip_records(
        db_session,
        trip_status=TripStatus.IN_PROGRESS,
    )

    cancelled_trip = TripService(db_session).cancel_trip(
        trip.id,
        TripCancellationRequest(
            reason="Vehicle returned because the route was closed.",
        ),
    )

    assert cancelled_trip.status == TripStatus.CANCELLED
    assert vehicle.status == VehicleStatus.AVAILABLE
    assert driver.status == DriverStatus.AVAILABLE


def test_completed_trip_cannot_be_cancelled(
    db_session: Session,
) -> None:
    trip, _, _ = create_trip_records(
        db_session,
        trip_status=TripStatus.COMPLETED,
    )

    with pytest.raises(HTTPException) as exception:
        TripService(db_session).cancel_trip(
            trip.id,
            TripCancellationRequest(
                reason="Invalid cancellation attempt.",
            ),
        )

    assert exception.value.status_code == 409
    assert exception.value.detail == ("A completed trip cannot be cancelled.")
