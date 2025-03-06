from uuid import UUID


class ScheduleQuery:
    def __init__(self, page_size: int, page_number: int, account_id: UUID | None):
        self.page_size = page_size
        self.page_number = page_number
        self.account_id = account_id

    def offset(self) -> int:
        return self.page_number * self.page_size

    def limit(self) -> int:
        return self.page_size

    def has_account_filter(self):
        return self.account_id is not None
