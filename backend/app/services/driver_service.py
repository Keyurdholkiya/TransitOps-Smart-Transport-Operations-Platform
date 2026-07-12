from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.fleet_enums import DriverStatus
from app.repositories.driver_repository import DriverRepository
from app.schemas.driver import DriverCreate, DriverUpdate


class DriverService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = DriverRepository(session)

    def create_driver(self, driver_data: DriverCreate) -> Driver:
        self._check_unique_fields(driver_data)

        try:
            driver = self.repository.create(driver_data)

            if driver.licence_expiry_date < date.today():
                driver.status = DriverStatus.INACTIVE

            self.session.commit()
            self.session.refresh(driver)
            return driver
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Driver employee code, licence, or email already exists.",
            ) from exc

    def get_driver(self, driver_id: UUID) -> Driver:
        driver = self.repository.get_by_id(driver_id)

        if driver is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found.",
            )

        return driver

    def list_drivers(
        self,
        *,
        offset: int,
        limit: int,
        driver_status: DriverStatus | None,
    ) -> tuple[list[Driver], int]:
        drivers = list(
            self.repository.list_drivers(
                offset=offset,
                limit=limit,
                status=driver_status,
            ),
        )
        total = self.repository.count_drivers(status=driver_status)

        return drivers, total

    def update_driver(
        self,
        driver_id: UUID,
        driver_data: DriverUpdate,
    ) -> Driver:
        driver = self.get_driver(driver_id)

        if driver.status == DriverStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A driver currently on a trip cannot be modified.",
            )

        changes = driver_data.model_dump(exclude_unset=True)

        if not changes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one driver field must be provided.",
            )

        non_nullable_fields = {
            "employee_code",
            "full_name",
            "phone_number",
            "licence_number",
            "licence_category",
            "licence_expiry_date",
            "joining_date",
        }

        if any(
            field_name in non_nullable_fields and value is None
            for field_name, value in changes.items()
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Required driver fields cannot be null.",
            )

        self._check_update_uniqueness(driver, changes)

        for field_name, value in changes.items():
            if field_name == "email" and value is not None:
                value = str(value)
            setattr(driver, field_name, value)

        if (
            driver.licence_expiry_date < date.today()
            and driver.status == DriverStatus.AVAILABLE
        ):
            driver.status = DriverStatus.INACTIVE

        try:
            driver = self.repository.save(driver)
            self.session.commit()
            self.session.refresh(driver)
            return driver
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Driver employee code, licence, or email already exists.",
            ) from exc

    def update_status(
        self,
        driver_id: UUID,
        new_status: DriverStatus,
    ) -> Driver:
        driver = self.get_driver(driver_id)

        if driver.status == new_status:
            return driver

        if driver.status == DriverStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trip status must be changed through trip operations.",
            )

        if new_status == DriverStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A driver can enter on-trip status only through dispatch.",
            )

        if (
            new_status == DriverStatus.AVAILABLE
            and driver.licence_expiry_date < date.today()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A driver with an expired licence cannot be available.",
            )

        driver.status = new_status
        driver = self.repository.save(driver)
        self.session.commit()
        self.session.refresh(driver)

        return driver

    def _check_unique_fields(self, driver_data: DriverCreate) -> None:
        if self.repository.get_by_employee_code(driver_data.employee_code):
            self._raise_duplicate("employee code")

        if self.repository.get_by_licence_number(driver_data.licence_number):
            self._raise_duplicate("licence number")

        if driver_data.email and self.repository.get_by_email(str(driver_data.email)):
            self._raise_duplicate("email")

    def _check_update_uniqueness(
        self,
        driver: Driver,
        changes: dict[str, object],
    ) -> None:
        employee_code = changes.get("employee_code")
        if isinstance(employee_code, str):
            existing = self.repository.get_by_employee_code(employee_code)
            if existing is not None and existing.id != driver.id:
                self._raise_duplicate("employee code")

        licence_number = changes.get("licence_number")
        if isinstance(licence_number, str):
            existing = self.repository.get_by_licence_number(licence_number)
            if existing is not None and existing.id != driver.id:
                self._raise_duplicate("licence number")

        email = changes.get("email")
        if email is not None:
            existing = self.repository.get_by_email(str(email))
            if existing is not None and existing.id != driver.id:
                self._raise_duplicate("email")

    @staticmethod
    def _raise_duplicate(field_name: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A driver with this {field_name} already exists.",
        )
