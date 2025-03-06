from typing import Literal

from pydantic import (
    PostgresDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_ignore_empty=True,
        extra='ignore',
    )

    PROJECT_NAME: str = 'exam reservation system'

    # env
    ENVIRONMENT: Literal['local', 'prod'] = 'local'

    # auth
    # 8 days = 60 minutes * 24 hours * 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SECRET_KEY: str = 'grepp'
    AUTHENTICATE_URL_PREFIX: list[str] = ['/schedules']
    ADMIN_URL_PREFIX: list[str] = ['/admin']

    DOCS_URL: str = '/docs'

    # database
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'grepp'
    POSTGRES_PASSWORD: str = 'grepp'
    POSTGRES_DB: str = 'grepp'

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        )

    def is_local(self) -> bool:
        return self.ENVIRONMENT == 'local'


env = Settings()
