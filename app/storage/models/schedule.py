from datetime import datetime
from uuid import UUID

from sqlalchemy import Column
from sqlmodel import Field, SQLModel, Relationship

from app.common.exceptions import BusinessException, ErrorCode, AuthorizationException
from app.service.models.schedule_form import ScheduleForm
from app.service.models.schedule_status import ScheduleStatus
from app.service.models.time_range import TimeRange
from app.storage.enum_convertor import EnumConvertor
from app.storage.models.account import Account


class Schedule(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    name: str = Field(max_length=100)
    start_at: datetime = Field(nullable=False)
    end_at: datetime = Field(nullable=False)
    applicants: int
    status: ScheduleStatus = Field(
        sa_column=Column(EnumConvertor(ScheduleStatus), nullable=False)
    )
    created_at: datetime | None = Field(default_factory=datetime.now)
    account_id: UUID = Field(foreign_key="account.id")
    account: Account = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    @staticmethod
    def from_form(schedule_form: ScheduleForm, account: Account) -> "Schedule":
        return Schedule(
            id=None,
            name=schedule_form.name,
            start_at=schedule_form.start_at,
            end_at=schedule_form.end_at,
            applicants=schedule_form.applicants,
            status=ScheduleStatus.PENDING,
            created_at=None,
            account_id=account.id,
            account=account,
        )

    def time_range(self) -> TimeRange:
        return TimeRange(start_at=self.start_at, end_at=self.end_at)

    def update(self, form: ScheduleForm) -> None:
        if self.__is_canceled():
            raise BusinessException(
                f"Can't update schedule while in CANCELED status.",
                ErrorCode.INVALID_STATE,
            )
        self.name = form.name
        self.start_at = form.start_at
        self.end_at = form.end_at
        self.applicants = form.applicants

    def validate_customer_cancel(self, requester_id: UUID) -> None:
        self.validate_owner(requester_id)
        if not self.__is_pending():
            raise BusinessException(
                f"schedule can't change status '{self.status.value}' to 'CANCEL'",
                ErrorCode.INVALID_STATE,
            )

    def change_status(self, to_be: ScheduleStatus) -> None:
        if to_be == ScheduleStatus.CANCELED:
            self.cancel()
        elif to_be == ScheduleStatus.CONFIRMED:
            self.__confirm()
        elif to_be == ScheduleStatus.PENDING:
            raise BusinessException(
                f"schedule can't change status '{self.status.value}' to 'PENDING'",
                ErrorCode.INVALID_ARGUMENT,
            )

    def validate_owner(self, account_id: UUID) -> None:
        if not self.__is_owner(account_id):
            raise AuthorizationException(
                f"schedule changes only owner. your are not this schedule owner. schedule_id: '{self.id}'"
            )

    def is_slot_allocated(self):
        return self.status == ScheduleStatus.CONFIRMED

    def cancel(self) -> None:
        self.status = ScheduleStatus.CANCELED

    def __is_pending(self):
        return self.status == ScheduleStatus.PENDING

    def __is_canceled(self) -> bool:
        return self.status == ScheduleStatus.CANCELED

    def __is_owner(self, account_id: UUID) -> bool:
        return self.account_id == account_id

    def __change_status(self, status: ScheduleStatus) -> None:
        self.status = status

    def __confirm(self) -> None:
        self.status = ScheduleStatus.CONFIRMED
