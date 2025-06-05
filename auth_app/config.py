import os

import dotenv
from pydantic import BaseModel, SecretStr

dotenv.load_dotenv()


class Settings(BaseModel):
    # POSTGRES
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    POSTGRES_DB: str
    # REDIS
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: SecretStr
    # PASSWORD HASHING
    HASHING_ALGORITHM: SecretStr
    HASHING_DEPRECATED: SecretStr
    # JWT SECRET KEY
    KEY: SecretStr
    # LOCALSTACK
    SERVICES: str
    AWS_ENDPOINT: str
    AWS_DEFAULT_REGION: str
    LOCALSTACK_HOST: str
    DEBUG: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    @property
    def postgres_dsn(self) -> str:
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql+asyncpg://" \
               f"{self.POSTGRES_USER}:{password}" \
               f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}" \
               f"/{self.POSTGRES_DB}"

    @property
    def sync_postgres_dsn(self) -> str:
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql+psycopg2://" \
               f"{self.POSTGRES_USER}:{password}" \
               f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}" \
               f"/{self.POSTGRES_DB}"

    @property
    def redis_dsn(self) -> str:
        password = self.REDIS_PASSWORD.get_secret_value()
        return f"redis://:{password}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def jwt_key(self) -> str:
        return self.KEY.get_secret_value()

    @property
    def hashing_algorithm(self) -> tuple[str, str]:
        """Returns tuple with HASHING_ALGORITHM and HASHING_DEPRECATED"""
        algorithm_v = self.HASHING_ALGORITHM.get_secret_value()
        deprecated_v = self.HASHING_DEPRECATED.get_secret_value()
        return algorithm_v, deprecated_v


POSTGRES_CONFIG = {
    "POSTGRES_USER": os.getenv("POSTGRES_USER", "pg_user"),
    "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "pg_pass"),
    "POSTGRES_DB": os.getenv("POSTGRES_DB", "pg"),
    "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "db"),
    "POSTGRES_PORT": int(os.getenv("POSTGRES_PORT", "5432")),
}

REDIS_CONFIG = {
    "REDIS_HOST": os.getenv("REDIS_HOST", "db_redis"),
    "REDIS_PORT": int(os.getenv("REDIS_PORT", "6379")),
    "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD", "redis_pass"),
}

PASSWORD_HASHING = {
    "HASHING_ALGORITHM": os.getenv("HASHING_ALGORITHM", "bcrypt"),
    "HASHING_DEPRECATED": os.getenv("HASHING_DEPRECATED", "auto"),
}
JWT_KEY = {
    "KEY": os.getenv("KEY", "simple_key_123"),
}
LOCALSTACK = {
    "SERVICES": os.getenv("SERVICES", "ses, s3"),
    "AWS_ENDPOINT": os.getenv("AWS_ENDPOINT", "http://localstack:4566"),
    "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    "LOCALSTACK_HOST": os.getenv("LOCALSTACK_HOST", "localstack"),
    "DEBUG": os.getenv("DEBUG", "1"),
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", "test"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
}

settings = Settings(
    **POSTGRES_CONFIG,
    **REDIS_CONFIG,
    **PASSWORD_HASHING,
    **JWT_KEY,
    **LOCALSTACK,
)
