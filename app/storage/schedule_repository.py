from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.service.models.page import SchedulePage
from app.service.models.schedule_query import ScheduleQuery
from app.storage.models.schedule import Schedule


class ScheduleRepository:
    def __init__(self, sess: AsyncSession):
        self.sess = sess

    async def save(self, schedule: Schedule) -> Schedule:
        self.sess.add(schedule)
        await self.sess.flush()
        return schedule

    async def find_by_id(self, schedule_id: int) -> Schedule | None:
        return await self.sess.get(Schedule, schedule_id)

    async def find_all(self, query: ScheduleQuery) -> SchedulePage:
        filter_account = Schedule.account_id == query.account_id if query.has_account_filter() else True

        list_query = select(Schedule).filter(filter_account).offset(query.offset()).limit(query.limit())
        schedules: list[Schedule] = (await self.sess.exec(list_query)).all()

        total_query = select(func.count()).select_from(Schedule).filter(filter_account)
        total = (await self.sess.exec(total_query)).one()

        return SchedulePage(
            total=total,
            page_size=query.page_size,
            page_number=query.page_number,
            items=schedules
        )
