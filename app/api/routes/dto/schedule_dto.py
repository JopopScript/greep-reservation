from datetime import datetime, timedelta

from pydantic import BaseModel, field_validator, model_validator

from app.api.routes.dto.account_dto import ProfileResponse
from app.common.exceptions import BusinessException, ErrorCode
from app.service.models.schedule_form import ScheduleForm
from app.service.models.schedule_status import ScheduleStatus
from app.storage.models.schedule import Schedule


class ScheduleResponse(BaseModel):
    id: int
    name: str
    start_at: datetime
    end_at: datetime
    applicants: int
    status: ScheduleStatus
    profile: ProfileResponse

    @staticmethod
    def from_schedule(schedule: Schedule) -> "ScheduleResponse":
        return ScheduleResponse(
            id=schedule.id,
            name=schedule.name,
            start_at=schedule.start_at,
            end_at=schedule.end_at,
            applicants=schedule.applicants,
            status=schedule.status,
            profile=ProfileResponse.from_account(schedule.account),
        )


class PaginatedScheduleResponse(BaseModel):
    total: int
    page_number: int  # 0부터 시작
    page_size: int
    items: list[ScheduleResponse]


ALLOWED_START_BEFORE: float = 3
APPLICANTS_LIMIT: int = 50_000


class ScheduleRequest(BaseModel):
    name: str
    start_at: datetime
    end_at: datetime
    applicants: int

    @field_validator("start_at")
    @classmethod
    def start_at_must_be_within_days(cls, start_at: datetime):
        allowed_date = datetime.now().date() + timedelta(days=ALLOWED_START_BEFORE)
        date = start_at.date()
        if date < allowed_date:
            raise BusinessException(
                f"schedule start_at must be at least {ALLOWED_START_BEFORE} days from today.",
                ErrorCode.INVALID_ARGUMENT,
            )
        return start_at

    @field_validator("start_at", "end_at")
    @classmethod
    def must_be_hourly(cls, d: datetime):
        if d.minute != 0 or d.second != 0 or d.microsecond != 0:
            raise BusinessException(
                "Time must be set at the beginning of an hour (e.g., 12:00:00).",
                ErrorCode.INVALID_ARGUMENT,
            )
        return d

    @field_validator("applicants")
    @classmethod
    def applicants_limit(cls, applicants: int):
        if applicants > APPLICANTS_LIMIT:
            raise BusinessException(
                "Applicants must be less than or equal to the limit. "
                + f"limit({APPLICANTS_LIMIT}) < applicants({applicants}).",
                ErrorCode.INVALID_ARGUMENT,
            )
        return applicants

    @model_validator(mode="after")
    @classmethod
    def validate_start_end_times(cls, request):
        start_at = request.start_at
        end_at = request.end_at
        if start_at >= end_at:
            raise BusinessException(
                "start time must be before end time.", ErrorCode.INVALID_ARGUMENT
            )
        return request

    def to_form(self) -> ScheduleForm:
        return ScheduleForm(
            name=self.name,
            start_at=self.start_at,
            end_at=self.end_at,
            applicants=self.applicants,
        )


class CustomerScheduleCancelRequest(BaseModel):
    status: ScheduleStatus

    @field_validator("status")
    @classmethod
    def must_be_cancel(cls, status: ScheduleStatus):
        if status != ScheduleStatus.CANCELED:
            raise BusinessException(
                "change status must be CANCELED.", ErrorCode.INVALID_ARGUMENT
            )
        return status


class AdminScheduleStatusChangeRequest(BaseModel):
    status: ScheduleStatus

    @field_validator("status")
    @classmethod
    def must_be_cancel(cls, status: ScheduleStatus):
        if status == ScheduleStatus.PENDING:
            raise BusinessException(
                "change status must not be PENDING.", ErrorCode.INVALID_ARGUMENT
            )
        return status
