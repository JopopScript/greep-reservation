from app.common.exceptions import BusinessException, ErrorCode
from app.service.models.schedule_status import ScheduleStatus
from app.storage.models.schedule import Schedule


class ScheduleStatusChange:
    def __init__(self, as_is_schedule: Schedule, to_be_status: ScheduleStatus):
        self.as_is_schedule: Schedule = as_is_schedule
        self.to_be_status: ScheduleStatus = to_be_status
        self.time_range = as_is_schedule.time_range()
        self.applicants = as_is_schedule.applicants
        self.__validate_equal()

    def __validate_equal(self):
        if self.__as_is_status == self.to_be_status:
            raise BusinessException(
                "as_is and to_be are the same. cant change to same status. "
                + f"status({self.__as_is_status()})",
                ErrorCode.INVALID_ARGUMENT,
            )

    def increase_applicants(self) -> bool:
        return (
            self.__as_is_status() != ScheduleStatus.CONFIRMED
            and self.to_be_status == ScheduleStatus.CONFIRMED
        )

    def decrease_applicants(self) -> bool:
        return (
            self.__as_is_status() == ScheduleStatus.CONFIRMED
            and self.to_be_status != ScheduleStatus.CONFIRMED
        )

    def __as_is_status(self):
        return self.as_is_schedule.status
