from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    drivers,
    health,
    info,
    trips,
    users,
    vehicles,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(info.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(vehicles.router)
api_router.include_router(drivers.router)
api_router.include_router(trips.router)
