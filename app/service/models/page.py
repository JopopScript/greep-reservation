from datetime import datetime

from app.storage.models.schedule import Schedule
from app.storage.models.schedule_slot import ScheduleSlot


class SchedulePage:
    def __init__(
        self, total: int, page_size: int, page_number: int, items: list[Schedule]
    ):
        self.total: int = total
        self.page_size: int = page_size
        self.page_number: int = page_number
        self.items: list[Schedule] = items


class ScheduleSlotPage:
    def __init__(self, items: list[ScheduleSlot]):
        self.items: list[ScheduleSlot] = items

    def start_at(self) -> datetime:
        return self.items[0].start_at()

    def end_at(self) -> datetime:
        return self.items[-1].end_at()
