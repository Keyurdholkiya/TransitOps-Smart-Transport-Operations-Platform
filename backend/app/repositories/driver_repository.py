from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.fleet_enums import DriverStatus
from app.schemas.driver import DriverCreate


class DriverRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, driver_id: UUID) -> Driver | None:
        return self.session.get(Driver, driver_id)

    def get_by_employee_code(self, employee_code: str) -> Driver | None:
        statement = select(Driver).where(
            Driver.employee_code == employee_code.strip().upper(),
        )
        return self.session.scalar(statement)

    def get_by_licence_number(self, licence_number: str) -> Driver | None:
        statement = select(Driver).where(
            Driver.licence_number == licence_number.strip().upper(),
        )
        return self.session.scalar(statement)

    def get_by_email(self, email: str) -> Driver | None:
        statement = select(Driver).where(
            Driver.email == email.strip().lower(),
        )
        return self.session.scalar(statement)

    def list_drivers(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        status: DriverStatus | None = None,
    ) -> Sequence[Driver]:
        statement = select(Driver)

        if status is not None:
            statement = statement.where(Driver.status == status)

        statement = (
            statement.order_by(
                Driver.created_at.desc(),
                Driver.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        return self.session.scalars(statement).all()

    def count_drivers(
        self,
        *,
        status: DriverStatus | None = None,
    ) -> int:
        statement = select(func.count()).select_from(Driver)

        if status is not None:
            statement = statement.where(Driver.status == status)

        return self.session.scalar(statement) or 0

    def create(self, driver_data: DriverCreate) -> Driver:
        driver = Driver(
            employee_code=driver_data.employee_code,
            full_name=driver_data.full_name,
            email=str(driver_data.email) if driver_data.email else None,
            phone_number=driver_data.phone_number,
            licence_number=driver_data.licence_number,
            licence_category=driver_data.licence_category,
            licence_expiry_date=driver_data.licence_expiry_date,
            joining_date=driver_data.joining_date,
            status=DriverStatus.AVAILABLE,
        )

        self.session.add(driver)
        self.session.flush()
        self.session.refresh(driver)

        return driver

    def save(self, driver: Driver) -> Driver:
        self.session.add(driver)
        self.session.flush()
        self.session.refresh(driver)

        return driver
