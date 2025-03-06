from fastapi import APIRouter

from app.api.routes import account_router, schedule_router, schedule_slot_router, admin_schedule_router, \
    health_check_router

api_router = APIRouter()
api_router.include_router(health_check_router.router)
api_router.include_router(account_router.router)
api_router.include_router(schedule_router.router)
api_router.include_router(admin_schedule_router.router)
api_router.include_router(schedule_slot_router.router)
