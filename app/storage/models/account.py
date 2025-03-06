from uuid import UUID

from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from app.service.models.role import Role
from app.storage.enum_convertor import EnumConvertor


class Account(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    nickname: str = Field(max_length=100)
    role: Role = Field(sa_column=Column(EnumConvertor(Role), nullable=False))
