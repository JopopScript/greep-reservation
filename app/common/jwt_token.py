from datetime import datetime, timedelta
from uuid import UUID

import jwt

from app.common.enviroment import env
from app.common.exceptions import AuthenticateException
from app.service.models.role import Role


class Authentication:
    def __init__(self, account_id: UUID, role: Role):
        self.account_id: UUID = account_id
        self.role: Role = role


class JwtTokenUtil:
    ALGORITHM: str = 'HS256'

    def create_access_token(self, auth: Authentication):
        auth_and_exp = {
            'sub': str(auth.account_id),
            'role': auth.role.value,
            'exp': datetime.now() + timedelta(minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(auth_and_exp, env.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_access_token(self, token: str) -> Authentication:
        payload = self.__parse_token(token)
        account_id: UUID = self.__parse_sub(payload.get('sub'))
        role: Role = self.__parse_role(payload.get('role'))
        return Authentication(account_id=account_id, role=role)

    def __parse_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, env.SECRET_KEY, algorithms=[self.ALGORITHM])
        except Exception:
            raise AuthenticateException('invalid token')

    @staticmethod
    def __parse_sub(user_id: str) -> UUID:
        try:
            return UUID(user_id)
        except ValueError:
            raise AuthenticateException(f"Invalid sub. is not UUID format. sub:'{user_id}'")

    @staticmethod
    def __parse_role(role: str) -> Role:
        try:
            return Role(role)
        except ValueError:
            raise AuthenticateException("Invalid role. is not exist role. role: '{role}'")


jwt_token_util = JwtTokenUtil()
