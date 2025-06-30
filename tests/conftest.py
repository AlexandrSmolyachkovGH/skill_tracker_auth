from unittest.mock import (
    AsyncMock,
    Mock,
)

import pytest

from auth_app.services.users import UserService


@pytest.fixture
def fake_env(monkeypatch):
    # POSTGRES DB
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_pwd")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5439")

    # REDIS
    monkeypatch.setenv("REDIS_PASSWORD", "test_pwd")
    monkeypatch.setenv("REDIS_PORT", "6380")
    monkeypatch.setenv("REDIS_HOST", "localhost")

    # PASSWORD HASHING
    monkeypatch.setenv("HASHING_ALGORITHM", "test_alg")
    monkeypatch.setenv("HASHING_DEPRECATED", "test_depr")

    # JWT SECRET KEY
    monkeypatch.setenv("KEY", "123")
    monkeypatch.setenv("ALGORITHM", "test_alg")
    monkeypatch.setenv("REFRESH_LASTING", "3500")
    monkeypatch.setenv("ACCESS_LASTING", "500")
    monkeypatch.setenv("ADMIN_SECRET", "test_secret")

    # LOCALSTACK
    monkeypatch.setenv("SERVICES", "ses, s3")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "default")
    monkeypatch.setenv("LOCALSTACK_HOST", "localstack")
    monkeypatch.setenv("DEBUG", "1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret")
    monkeypatch.setenv("AWS_ENDPOINT", "http://localhost:4566")
    monkeypatch.setenv("RESET_PWD_LENGTH", "15")
    monkeypatch.setenv("VERIFICATION_CODE_LENGTH", "5")


@pytest.fixture
def mock_dependencies():
    return {
        "user_repo": Mock(
            create_user=AsyncMock(),
            get_user=AsyncMock(),
            update_user=AsyncMock(),
            get_users=AsyncMock(),
        ),
        "token_repo": Mock(
            create_refresh=AsyncMock(),
            get_refresh=AsyncMock(),
            update_refresh=AsyncMock(),
        ),
        "redis": Mock(),
        "ses": Mock(),
    }


@pytest.fixture
def user_service(mock_dependencies):
    return UserService(
        user_repo=mock_dependencies["user_repo"],
        token_repo=mock_dependencies["token_repo"],
        redis=mock_dependencies["redis"],
        ses=mock_dependencies["ses"],
    )
