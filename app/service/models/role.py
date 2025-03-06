from enum import Enum


class Role(str, Enum):
    CUSTOMER = 'CUSTOMER'
    ADMIN = 'ADMIN'
