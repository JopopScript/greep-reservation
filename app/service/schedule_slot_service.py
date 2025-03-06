from datetime import datetime

from app.common.exceptions import BusinessException, ErrorCode
from app.service.models.page import ScheduleSlotPage
from app.service.models.schedule_form import ScheduleForm
from app.service.models.schedule_slot_query import ScheduleSlotQuery
from app.service.models.schedule_status_change import ScheduleStatusChange
from app.service.models.time_range import TimeRange
from app.storage.models.schedule import Schedule
from app.storage.models.schedule_slot import ScheduleSlot
from app.storage.schedule_slot_repository import ScheduleSlotRepository


class ScheduleSlotService:
    def __init__(self, repository: ScheduleSlotRepository):
        self.repository = repository

    async def get(self, start_at: datetime) -> ScheduleSlot:
        return await self.repository.find_by_start_at(start_at)

    async def page(self, query: ScheduleSlotQuery) -> ScheduleSlotPage:
        return await self.repository.find_page(query)

    async def re_allocate(self, as_is: Schedule, to_be: ScheduleForm) -> None:
        applicants = as_is.applicants
        await self.validate_applicants_limit(to_be.time_range(), applicants)
        if as_is.slot_allocated():
            await self.repository.add_applicants(as_is.time_range(), -applicants)
            await self.repository.add_applicants(to_be.time_range(), applicants)

    async def add_or_minus_by(self, change_status: ScheduleStatusChange) -> None:
        time_range = change_status.time_range
        applicants = change_status.applicants
        if change_status.increase_applicants():
            await self.validate_applicants_limit(time_range, applicants)
            await self.repository.add_applicants(time_range, applicants)
        elif change_status.decrease_applicants():
            await self.repository.add_applicants(time_range, -applicants)

    async def validate_applicants_limit(self, time_range: TimeRange, applicants: int) -> None:
        remain = await self.repository.min_applicants_in_range(time_range)
        if remain < applicants:
            raise BusinessException(
                'Applicants must be less than or equal to the limit. ' +
                f'limit({remain}) < applicants({applicants}). range({time_range})',
                ErrorCode.INVALID_ARGUMENT
            )
