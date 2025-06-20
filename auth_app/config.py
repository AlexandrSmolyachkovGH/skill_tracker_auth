from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class PostgresSettings(BaseConfig):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    POSTGRES_DB: str

    @property
    def postgres_dsn(self) -> str:
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql+asyncpg://" \
               f"{self.POSTGRES_USER}:{password}" \
               f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}" \
               f"/{self.POSTGRES_DB}"


class RedisSettings(BaseConfig):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: SecretStr

    @property
    def redis_dsn(self) -> str:
        password = self.REDIS_PASSWORD.get_secret_value()
        return f"redis://:{password}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"


class JWTSettings(BaseConfig):
    KEY: SecretStr
    ALGORITHM: SecretStr
    REFRESH_LASTING: int
    ACCESS_LASTING: int
    ADMIN_SECRET: SecretStr

    @property
    def jwt_key(self) -> str:
        return self.KEY.get_secret_value()


class PasswordSettings(BaseConfig):
    HASHING_ALGORITHM: SecretStr
    HASHING_DEPRECATED: SecretStr

    @property
    def hashing_algorithm(self) -> tuple[str, str]:
        """Returns tuple with HASHING_ALGORITHM and HASHING_DEPRECATED"""
        algorithm_v = self.HASHING_ALGORITHM.get_secret_value()
        deprecated_v = self.HASHING_DEPRECATED.get_secret_value()
        return algorithm_v, deprecated_v


class AWSSettings(BaseConfig):
    SERVICES: str
    AWS_ENDPOINT: str
    AWS_DEFAULT_REGION: str
    LOCALSTACK_HOST: str
    DEBUG: str
    AWS_ACCESS_KEY_ID: SecretStr
    AWS_SECRET_ACCESS_KEY: SecretStr


pg_settings = PostgresSettings()
redis_settings = RedisSettings()
jwt_settings = JWTSettings()
pwd_settings = PasswordSettings()
aws_settings = AWSSettings()
