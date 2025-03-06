from enum import Enum
from typing import Type, TypeVar, Generic

from sqlalchemy import String, TypeDecorator

T = TypeVar('T', bound=Enum)


class EnumConvertor(TypeDecorator, Generic[T]):
    impl = String(20)

    def __init__(self, enum_type: Type[T]):
        super().__init__()
        self.enum_type = enum_type

    def process_bind_param(self, value: T, dialect) -> str:
        return value.value if isinstance(value, self.enum_type) else value

    def process_result_value(self, value: str, dialect) -> T:
        return self.enum_type(value) if value else None
