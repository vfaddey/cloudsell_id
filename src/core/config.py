from typing import Optional

from pydantic import UUID4
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: Optional[str] = "CloudSell.ID Service"
    DB_TYPE: str = "postgresql"
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_DRIVER: str = 'asyncpg'

    JWT_PRIVATE_KEY_PATH: Path
    JWT_PUBLIC_KEY_PATH: Path
    JWT_ALGORITHM: str = "RS256"

    ACCESS_TOKEN_LIFETIME: int = 60 # minutes
    REFRESH_TOKEN_LIFETIME: int = 30 # days
    CONFIRMATION_TOKEN_LIFETIME: int = 1 # day

    #rabbit
    RABBITMQ_URL: str
    RABBITMQ_QUEUE: str

    __private_key = None
    __public_key = None

    class Config:
        env_file = ".env"
        extra = 'ignore'

    @property
    def DB_URL(self):
        return f'{self.DB_TYPE}+{self.DB_DRIVER}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}'

    @property
    def JWT_PRIVATE_KEY(self):
        if not self.__private_key:
            with open(self.JWT_PRIVATE_KEY_PATH) as f:
                self.__private_key = f.read()
                return self.__private_key
        return self.__private_key

    @property
    def JWT_PUBLIC_KEY(self):
        if not self.__public_key:
            with open(self.JWT_PUBLIC_KEY_PATH) as f:
                self.__public_key = f.read()
                return self.__public_key
        return self.__public_key


class Templates(BaseSettings):
    CONFIRMATION_EMAIL_TEMPLATE: UUID4
    RESET_PASSWORD_EMAIL_TEMPLATE: UUID4

    class Config:
        env_file = ".env.templates"

settings = Settings()
email_settings = Templates()


