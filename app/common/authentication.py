from uuid import UUID

from app.service.models.role import Role


class Authentication:
    ANONYMOUS = None

    def __init__(self, account_id: UUID | None, role: Role | None):
        self.account_id: UUID = account_id
        self.role: Role = role

    def is_anonymous(self):
        return self == Authentication.ANONYMOUS

    def is_customer(self):
        return self.role == Role.CUSTOMER

    def is_admin(self):
        return self.role == Role.ADMIN

    @staticmethod
    def anonymous():
        return Authentication.ANONYMOUS


Authentication.ANONYMOUS = Authentication(account_id=None, role=None)
