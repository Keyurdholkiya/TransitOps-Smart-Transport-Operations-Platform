from enum import StrEnum


class TripStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TripType(StrEnum):
    DELIVERY = "delivery"
    PICKUP = "pickup"
    TRANSFER = "transfer"
    OTHER = "other"
