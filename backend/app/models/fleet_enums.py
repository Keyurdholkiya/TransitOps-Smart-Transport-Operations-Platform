from enum import StrEnum


class VehicleStatus(StrEnum):
    AVAILABLE = "available"
    ON_TRIP = "on_trip"
    IN_SHOP = "in_shop"
    RETIRED = "retired"


class VehicleType(StrEnum):
    TRUCK = "truck"
    VAN = "van"
    TRAILER = "trailer"
    PICKUP = "pickup"
    OTHER = "other"


class DriverStatus(StrEnum):
    AVAILABLE = "available"
    ON_TRIP = "on_trip"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
