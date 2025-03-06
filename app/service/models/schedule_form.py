from datetime import datetime

from app.service.models.time_range import TimeRange


class ScheduleForm:
    def __init__(
        self, name: str, start_at: datetime, end_at: datetime, applicants: int
    ):
        self.name: str = name
        self.start_at: datetime = start_at
        self.end_at: datetime = end_at
        self.applicants: int = applicants

    def time_range(self) -> TimeRange:
        return TimeRange(start_at=self.start_at, end_at=self.end_at)
