from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.api.routes.dto.schedule_slot_dto import PaginatedScheduleSlotResponse, ScheduleSlotResponse
from app.dependencies import schedule_slot_service
from app.docs.error_responses import get_schedule_slots
from app.service.models.schedule_slot_query import ScheduleSlotQuery
from app.service.schedule_slot_service import ScheduleSlotService

router = APIRouter(tags=['schedule-slot'])


@router.get(
    '/schedule-slot',
    response_model=PaginatedScheduleSlotResponse,
    responses=get_schedule_slots
)
async def get_schedule_slot(
        start_at: datetime | None = Query(alias='start-at'),
        end_at: datetime | None = Query(alias='end-at'),
        service: ScheduleSlotService = Depends(schedule_slot_service),
) -> PaginatedScheduleSlotResponse:
    schedule_slots = await service.page(ScheduleSlotQuery(start_at=start_at, end_at=end_at))
    return PaginatedScheduleSlotResponse(
        start_at=schedule_slots.start_at(),
        end_at=schedule_slots.end_at(),
        items=[ScheduleSlotResponse.fromScheduleSlot(slot) for slot in schedule_slots.items]
    )
