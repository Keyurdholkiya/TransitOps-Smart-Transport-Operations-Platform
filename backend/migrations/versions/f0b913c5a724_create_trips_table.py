"""create trips table

Revision ID: f0b913c5a724
Revises: d637f1379e00
Create Date: 2026-07-12

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f0b913c5a724"
down_revision: str | Sequence[str] | None = "d637f1379e00"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the trips table."""
    op.create_table(
        "trips",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("trip_number", sa.String(length=50), nullable=False),
        sa.Column("vehicle_id", sa.UUID(), nullable=False),
        sa.Column("driver_id", sa.UUID(), nullable=False),
        sa.Column(
            "trip_type",
            sa.Enum(
                "delivery",
                "pickup",
                "transfer",
                "other",
                name="trip_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column(
            "cargo_weight_kg",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "planned",
                "in_progress",
                "completed",
                "cancelled",
                name="trip_status",
                native_enum=False,
                create_constraint=True,
            ),
            server_default="planned",
            nullable=False,
        ),
        sa.Column(
            "scheduled_departure_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "dispatched_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "cancellation_reason",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "final_odometer_km",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "cargo_weight_kg > 0",
            name="ck_trips_cargo_weight_positive",
        ),
        sa.CheckConstraint(
            "final_odometer_km IS NULL OR final_odometer_km >= 0",
            name="ck_trips_final_odometer_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["drivers.id"],
            name=op.f("fk_trips_driver_id_drivers"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.id"],
            name=op.f("fk_trips_vehicle_id_vehicles"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_trips"),
        ),
        sa.UniqueConstraint(
            "trip_number",
            name=op.f("uq_trips_trip_number"),
        ),
    )

    op.create_index(
        op.f("ix_trips_driver_id"),
        "trips",
        ["driver_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_trips_status"),
        "trips",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_trips_vehicle_id"),
        "trips",
        ["vehicle_id"],
        unique=False,
    )
    op.create_index(
        "uq_trips_active_driver",
        "trips",
        ["driver_id"],
        unique=True,
        postgresql_where=sa.text("status = 'in_progress'"),
    )
    op.create_index(
        "uq_trips_active_vehicle",
        "trips",
        ["vehicle_id"],
        unique=True,
        postgresql_where=sa.text("status = 'in_progress'"),
    )


def downgrade() -> None:
    """Remove the trips table."""
    op.drop_index(
        "uq_trips_active_vehicle",
        table_name="trips",
        postgresql_where=sa.text("status = 'in_progress'"),
    )
    op.drop_index(
        "uq_trips_active_driver",
        table_name="trips",
        postgresql_where=sa.text("status = 'in_progress'"),
    )
    op.drop_index(
        op.f("ix_trips_vehicle_id"),
        table_name="trips",
    )
    op.drop_index(
        op.f("ix_trips_status"),
        table_name="trips",
    )
    op.drop_index(
        op.f("ix_trips_driver_id"),
        table_name="trips",
    )
    op.drop_table("trips")
