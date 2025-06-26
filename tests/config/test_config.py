from pydantic_settings import BaseSettings

from auth_app.config import (
    AWSSettings,
    BaseConfig,
    JWTSettings,
    PasswordSettings,
    PostgresSettings,
    RedisSettings,
)
from tests.conftest import (
    fake_env,
)


def test_base_conf() -> None:
    assert issubclass(BaseConfig, BaseSettings)


def test_pg_settings(fake_env) -> None:
    pg_settings = PostgresSettings()
    assert pg_settings.postgres_dsn == "postgresql+asyncpg://test_user:test_pwd@localhost:5439/test_db"


def test_redis_settings(fake_env) -> None:
    redis_settings = RedisSettings()
    assert redis_settings.redis_dsn == "redis://:test_pwd@localhost:6380/0"


def test_jwt_settings(fake_env) -> None:
    jwt_settings = JWTSettings()
    assert str(jwt_settings.jwt_key) == "123"
    assert jwt_settings.ADMIN_SECRET.get_secret_value() == "test_secret"
    assert jwt_settings.ALGORITHM.get_secret_value() == "test_alg"


def test_pwd_settings(fake_env) -> None:
    pwd_settings = PasswordSettings()
    assert pwd_settings.HASHING_ALGORITHM.get_secret_value() == "test_alg"
    assert pwd_settings.HASHING_DEPRECATED.get_secret_value() == "test_depr"


def test_aws_settings(fake_env) -> None:
    aws_settings = AWSSettings()
    assert aws_settings.AWS_ENDPOINT == "http://localhost:4566"
    assert aws_settings.AWS_DEFAULT_REGION == "default"
    assert aws_settings.AWS_SECRET_ACCESS_KEY.get_secret_value() == "test_secret"
