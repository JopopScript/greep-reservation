from uuid import UUID

from app.common.exceptions import NoResourceException
from app.service.account_service import AccountService
from app.service.models.page import SchedulePage
from app.service.models.schedule_form import ScheduleForm
from app.service.models.schedule_query import ScheduleQuery
from app.service.models.schedule_status import ScheduleStatus
from app.service.models.schedule_status_change import ScheduleStatusChange
from app.service.schedule_slot_service import ScheduleSlotService
from app.storage.models.schedule import Schedule
from app.storage.schedule_repository import ScheduleRepository


class ScheduleService:
    def __init__(self, repository: ScheduleRepository, slot_service: ScheduleSlotService,
                 account_service: AccountService):
        self.repository = repository
        self.slot_service = slot_service
        self.account_service = account_service

    async def list(self, query: ScheduleQuery) -> SchedulePage:
        return await self.repository.find_all(query)

    async def create(self, account_id: UUID, form: ScheduleForm) -> Schedule:
        account = await self.account_service.get_or_raise(account_id)
        schedule = Schedule.from_form(form, account)
        await self.slot_service.validate_applicants_limit(schedule.time_range(), schedule.applicants)
        return await self.repository.save(schedule)

    async def customer_update(self, schedule_id: int, form: ScheduleForm, account_id: UUID) -> Schedule:
        schedule = await self.__get_or_raise(schedule_id)
        schedule.validate_owner(account_id)
        await self.slot_service.re_allocate(schedule, form)
        schedule.update(form)
        return await self.repository.save(schedule)

    async def admin_update(self, schedule_id: int, form: ScheduleForm) -> Schedule:
        schedule = await self.__get_or_raise(schedule_id)
        await self.slot_service.re_allocate(schedule, form)
        schedule.update(form)
        return await self.repository.save(schedule)

    async def customer_cancel(self, account_id: UUID, schedule_id: int) -> Schedule:
        schedule = await self.__get_or_raise(schedule_id)
        schedule.validate_owner(account_id)
        schedule.validate_customer_cancel(account_id)
        await self.slot_service.add_or_minus_by(ScheduleStatusChange(schedule, ScheduleStatus.CANCELED))
        schedule.cancel()
        return await self.repository.save(schedule)

    async def admin_change_status(self, schedule_id: int, to_be: ScheduleStatus) -> Schedule:
        schedule = await self.__get_or_raise(schedule_id)
        await self.slot_service.add_or_minus_by(ScheduleStatusChange(schedule, to_be))
        schedule.change_status(to_be)
        return schedule

    async def __get_or_raise(self, schedule_id: int) -> Schedule:
        schedule = await self.repository.find_by_id(schedule_id)
        if schedule is None:
            raise NoResourceException(f"schedule is not exists. schedule_id: '{schedule_id}'")
        return schedule
