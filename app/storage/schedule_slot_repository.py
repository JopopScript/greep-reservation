from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col, and_, update

from app.service.models.page import ScheduleSlotPage
from app.service.models.schedule_slot_query import ScheduleSlotQuery
from app.service.models.time_range import TimeRange
from app.storage.models.schedule_slot import ScheduleSlot


class ScheduleSlotRepository:
    def __init__(self, sess: AsyncSession):
        self.sess = sess

    async def find_by_start_at(self, start_at: datetime) -> ScheduleSlot:
        slot_start = self.align_hour(start_at)
        return await self._get_or_create_slot(slot_start)

    async def update_confirmed_applicants(
        self, slot_start: datetime, new_count: int
    ) -> ScheduleSlot:
        slot = await self._get_or_create_slot(slot_start)
        slot.confirmed_applicants = new_count

        self.sess.add(slot)
        await self.sess.flush()
        return slot

    async def find_schedules_by_range_with_lock(self, time_range: TimeRange) -> list[ScheduleSlot]:
        await self.__missing_create_slot(time_range.start_at(), time_range.end_at())
        query = (
            select(ScheduleSlot)
            .where(
                and_(
                    ScheduleSlot.slot_start_time >= time_range.start_at(),
                    ScheduleSlot.slot_start_time <= time_range.end_at(),
                    )
            )
            .order_by(ScheduleSlot.slot_start_time)
            .with_for_update()
        )

        async with self.sess.begin():  # Ensure we are inside a transaction
            result = await self.sess.exec(query)
            slots = result.all()

        return slots

    async def min_applicants_in_range(self, time_range: TimeRange) -> int:
        await self.__missing_create_slot(time_range.start_at(), time_range.end_at())
        query = (
            select(ScheduleSlot)
            .where(
                and_(
                    ScheduleSlot.slot_start_time >= time_range.start_at(),
                    ScheduleSlot.slot_start_time <= time_range.end_at(),
                    )
            )
            .order_by((ScheduleSlot.max_applicants - ScheduleSlot.confirmed_applicants))
            .limit(1)
        )

        result = await self.sess.exec(query)
        min_slot = result.first()
        return min_slot.max_applicants - min_slot.confirmed_applicants

    async def add_applicants(self, time_range: TimeRange, applicants: int) -> None:
        await self.__missing_create_slot(time_range.start_at(), time_range.end_at())
        stmt = (
            update(ScheduleSlot)
            .where(
                and_(
                    ScheduleSlot.slot_start_time >= time_range.start_at(),
                    ScheduleSlot.slot_start_time <= time_range.end_at(),
                )
            )
            .values(confirmed_applicants=ScheduleSlot.confirmed_applicants + applicants)
        )
        await self.sess.exec(stmt)

    async def _get_or_create_slot(self, slot_start: datetime) -> ScheduleSlot:
        stmt = select(ScheduleSlot).where(ScheduleSlot.slot_start_time == slot_start)
        result = await self.sess.execute(stmt)
        schedule_slot: ScheduleSlot | None = result.scalar_one_or_none()

        if schedule_slot is None:
            schedule_slot = ScheduleSlot(slot_start_time=slot_start)
            self.sess.add(schedule_slot)
            await self.sess.flush()
        return schedule_slot

    async def find_page(self, query: ScheduleSlotQuery) -> ScheduleSlotPage:
        await self.__missing_create_slot(query.start_at, query.end_at)
        schedule_slots = await self.__find_all(query.start_at, query.end_at)
        return ScheduleSlotPage(items=schedule_slots)

    async def __missing_create_slot(self, start_at: datetime, end_at: datetime) -> None:
        exist_slots = await self.__find_all(start_at, end_at)
        require_times = self.missing_slot(start_at, end_at, exist_slots)
        await self.__create_all(require_times)

    async def __find_all(
        self, start_at: datetime, end_at: datetime
    ) -> list[ScheduleSlot]:
        stmt = (
            select(ScheduleSlot)
            .where(
                ScheduleSlot.slot_start_time >= start_at,
                ScheduleSlot.slot_start_time < end_at,
            )
            .order_by(col(ScheduleSlot.slot_start_time))
        )
        result = await self.sess.exec(stmt)
        return result.all()

    async def __create_all(self, start_times: list[datetime]) -> None:
        if start_times:
            slots_to_create = [
                ScheduleSlot(slot_start_time=slot_time) for slot_time in start_times
            ]
            self.sess.add_all(slots_to_create)
            await self.sess.flush()

    def missing_slot(
        self, start_at: datetime, end_at: datetime, exists: list[ScheduleSlot]
    ):
        existing_slots = {s.slot_start_time for s in exists}
        missing_slot = []
        current_time = self.align_hour(start_at)
        while current_time < end_at:
            if current_time not in existing_slots:
                missing_slot.append(current_time)
            current_time += timedelta(hours=1)
        return missing_slot

    def align_hour(self, d: datetime) -> datetime:
        if d.minute == 0 and d.second == 0 and d.microsecond == 0:
            return d
        return (d + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
