from fastapi import APIRouter, Depends, Query

from app.api.routes.dto.schedule_dto import (
    ScheduleResponse,
    PaginatedScheduleResponse,
    ScheduleRequest,
    AdminScheduleStatusChangeRequest,
)
from app.dependencies import schedule_service
from app.docs.error_responses import admin_change_schedule, admin_change_schedule_status
from app.service.models.page import SchedulePage
from app.service.models.schedule_query import ScheduleQuery
from app.service.schedule_service import ScheduleService

router = APIRouter(tags=["admin/schedules"])


@router.get("/admin/schedules", response_model=PaginatedScheduleResponse)
async def get_schedules(
    page: int = Query(0, alias="page", ge=0),
    page_size: int = Query(10, alias="page-size", ge=1, le=100),
    service: ScheduleService = Depends(schedule_service),
) -> PaginatedScheduleResponse:
    schedule_page: SchedulePage = await service.list(
        ScheduleQuery(page_number=page, page_size=page_size, account_id=None)
    )
    return PaginatedScheduleResponse(
        total=schedule_page.total,
        page_number=schedule_page.page_number,
        page_size=schedule_page.page_size,
        items=[ScheduleResponse.from_schedule(s) for s in schedule_page.items],
    )


@router.put(
    "/admin/schedules/{schedule_id}",
    response_model=ScheduleResponse,
    responses=admin_change_schedule,
)
async def change_schedule(
    schedule_id: int,
    schedule_request: ScheduleRequest,
    service: ScheduleService = Depends(schedule_service),
) -> ScheduleResponse:
    schedule = await service.admin_update(schedule_id, schedule_request.to_form())
    return ScheduleResponse.from_schedule(schedule)


@router.put(
    "/admin/schedules/{schedule_id}/status",
    response_model=ScheduleResponse,
    responses=admin_change_schedule_status,
)
async def change_schedule_status(
    schedule_id: int,
    change_request: AdminScheduleStatusChangeRequest,
    service: ScheduleService = Depends(schedule_service),
) -> ScheduleResponse:
    schedule = await service.admin_change_status(schedule_id, change_request.status)
    return ScheduleResponse.from_schedule(schedule)
