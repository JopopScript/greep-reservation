from datetime import datetime

from pydantic import BaseModel

from app.storage.models.schedule_slot import ScheduleSlot


class ScheduleSlotResponse(BaseModel):
    start_at: datetime
    end_at: datetime
    max_applicants: int
    confirmed_applicants: int

    @staticmethod
    def fromScheduleSlot(slot: ScheduleSlot) -> 'ScheduleSlotResponse':
        return ScheduleSlotResponse(
            start_at=slot.start_at(),
            end_at=slot.end_at(),
            max_applicants=slot.max_applicants,
            confirmed_applicants=slot.confirmed_applicants,
        )


class PaginatedScheduleSlotResponse(BaseModel):
    start_at: datetime
    end_at: datetime
    items: list[ScheduleSlotResponse]
