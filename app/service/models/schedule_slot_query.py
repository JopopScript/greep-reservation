from datetime import datetime, timedelta

from app.common.exceptions import BusinessException, ErrorCode


class ScheduleSlotQuery:
    MAX_PERIOD_DAYS: int = 14
    ALLOWED_START_BEFORE: int = 3

    def __init__(self, start_at: datetime, end_at: datetime):
        self.start_at: datetime = start_at
        self.end_at: datetime = end_at

        self.__validate_min_start_at()
        self.__validate_time_order()
        self.__validate_max_period()

    def __validate_min_start_at(self):
        min_start_date = datetime.now().date() + timedelta(
            days=self.ALLOWED_START_BEFORE
        )
        if self.start_at.date() < min_start_date:
            raise BusinessException(
                f"schedule start_at must be at least {self.ALLOWED_START_BEFORE} days from today.",
                ErrorCode.INVALID_ARGUMENT,
            )

    def __validate_time_order(self):
        if self.end_at <= self.start_at:
            raise BusinessException(
                "start time must be before end time.", ErrorCode.INVALID_ARGUMENT
            )

    def __validate_max_period(self):
        max_end_date = self.start_at + timedelta(days=self.MAX_PERIOD_DAYS)
        if self.end_at > max_end_date:
            raise BusinessException(
                f"The search period cannot exceed {self.MAX_PERIOD_DAYS} days.",
                ErrorCode.INVALID_ARGUMENT,
            )
