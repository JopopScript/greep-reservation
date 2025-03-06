from fastapi import APIRouter, Depends, Request, Query

from app.api.routes.dto.schedule_dto import ScheduleResponse, ScheduleRequest, \
    PaginatedScheduleResponse, CustomerScheduleCancelRequest
from app.common.auth_middleware import account_id
from app.dependencies import schedule_service
from app.docs.error_responses import customer_create_schedule, customer_change_schedule, customer_change_schedule_status
from app.service.models.page import SchedulePage
from app.service.models.schedule_query import ScheduleQuery
from app.service.schedule_service import ScheduleService

router = APIRouter(tags=['schedules'])


@router.get('/schedules', response_model=PaginatedScheduleResponse)
async def get_schedules(
        request: Request,
        page: int = Query(0, alias='page', ge=0),
        page_size: int = Query(10, alias='page-size', ge=1, le=100),
        service: ScheduleService = Depends(schedule_service),
) -> PaginatedScheduleResponse:
    schedule_page: SchedulePage = await service.list(
        ScheduleQuery(
            page_number=page,
            page_size=page_size,
            account_id=account_id(request)
        ))
    return PaginatedScheduleResponse(
        total=schedule_page.total,
        page_number=schedule_page.page_number,
        page_size=schedule_page.page_size,
        items=[ScheduleResponse.fromSchedule(s) for s in schedule_page.items]
    )


@router.post(
    '/schedules',
    response_model=ScheduleResponse,
    responses=customer_create_schedule
)
async def create_schedule(
        request: Request,
        schedule_request: ScheduleRequest,
        service: ScheduleService = Depends(schedule_service)) -> ScheduleResponse:
    schedule = await service.create(account_id(request), schedule_request.to_form())
    return ScheduleResponse.fromSchedule(schedule)


@router.put(
    '/schedules/{schedule_id}',
    response_model=ScheduleResponse,
    responses=customer_change_schedule
)
async def change_schedule(
        request: Request,
        schedule_id: int,
        schedule_request: ScheduleRequest,
        service: ScheduleService = Depends(schedule_service)
) -> ScheduleResponse:
    schedule = await service.customer_update(schedule_id, schedule_request.to_form(), account_id(request))
    return ScheduleResponse.fromSchedule(schedule)


@router.put(
    '/schedules/{schedule_id}/status',
    response_model=ScheduleResponse,
    responses=customer_change_schedule_status
)
async def change_schedule_status(
        request: Request,
        schedule_id: int,
        update_request: CustomerScheduleCancelRequest,
        service: ScheduleService = Depends(schedule_service)
) -> ScheduleResponse:
    schedule = await service.customer_cancel(account_id(request), schedule_id)
    return ScheduleResponse.fromSchedule(schedule)
