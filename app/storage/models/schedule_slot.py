from datetime import datetime, timedelta

from sqlmodel import Field, SQLModel


class ScheduleSlot(SQLModel, table=True):
    __tablename__ = 'schedule_slot'

    id: int | None = Field(default=None, primary_key=True)
    slot_start_time: datetime = Field(nullable=False)
    max_applicants: int = Field(default=50000, nullable=False)
    confirmed_applicants: int = Field(default=0, nullable=False)

    def start_at(self) -> datetime:
        return self.slot_start_time

    def end_at(self) -> datetime:
        return self.slot_start_time + timedelta(hours=1)
