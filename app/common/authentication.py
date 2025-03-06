from uuid import UUID

from starlette.authentication import (AuthCredentials, BaseUser)

from app.service.models.role import Role


class Authentication(BaseUser):
    ANONYMOUS = None

    def __init__(self, account_id: UUID | None, role: Role | None):
        self.account_id: UUID = account_id
        self.role: Role = role

    def is_authenticated(self) -> bool:
        return self != Authentication.ANONYMOUS

    def is_customer(self):
        return self.role == Role.CUSTOMER

    def is_admin(self):
        return self.role == Role.ADMIN

    def auth_credentials(self) -> AuthCredentials:
        if not self.is_authenticated():
            return AuthCredentials([])
        return AuthCredentials([str(self.role.value)])

    @staticmethod
    def anonymous():
        return Authentication.ANONYMOUS


Authentication.ANONYMOUS = Authentication(account_id=None, role=None)
