from datetime import (
    datetime,
    timedelta,
)
from unittest.mock import (
    AsyncMock,
    MagicMock,
    Mock,
    patch,
)
from uuid import uuid4

import pytest
from redis.asyncio.client import Redis

from auth_app.models import UserORM
from auth_app.models.users import UserRole
from auth_app.schemes.email import EmailPayloadScheme
from auth_app.schemes.users import (
    CreateUserExtendedScheme,
    RoleEnum,
)
from auth_app.services.ses.ses_handler import ses_handler
from auth_app.services.users import UserService
from auth_app.services.utils.pwd_hashing import hash_password


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
def mock_user_repo():
    return Mock(
        create_user=AsyncMock(),
        get_user=AsyncMock(),
        update_user=AsyncMock(),
        get_users=AsyncMock(),
    )


@pytest.fixture
def mock_token_repo():
    return Mock(
        create_refresh=AsyncMock(),
        get_refresh=AsyncMock(),
        update_refresh=AsyncMock(),
    )


@pytest.fixture
def verification_code() -> str:
    return "123Code!"


@pytest.fixture
def mock_redis(
    verification_code
) -> Redis:
    mock = MagicMock()
    mock.set = AsyncMock(return_value=None)
    mock.get = AsyncMock(return_value=verification_code)
    return mock


@pytest.fixture
def mock_ses():
    return Mock()


@pytest.fixture
def mock_user_service(
    mock_user_repo,
    mock_token_repo,
    mock_redis,
    mock_ses
) -> UserService:
    return UserService(
        user_repo=mock_user_repo,
        token_repo=mock_token_repo,
        redis=mock_redis,
        ses=mock_ses,
    )


@pytest.fixture(scope="session")
def get_user_data() -> dict:
    email = "email@example.com"
    password = "12345Password!"
    hashed = hash_password(password)
    return {
        "email": email,
        "password": password,
        "password_hash": hashed,
    }


@pytest.fixture(scope="session")
def user_id():
    return uuid4()


@pytest.fixture
def get_user_orm(
    get_user_data,
    user_id
) -> UserORM:
    return UserORM(
        id=user_id,
        email=get_user_data["email"],
        password_hash=get_user_data["password_hash"],
        role=UserRole.USER,
        is_verified=False,
        is_active=True,
    )


@pytest.fixture
def get_verified_user_orm(
    get_user_data,
    user_id
) -> UserORM:
    return UserORM(
        id=user_id,
        email=get_user_data["email"],
        password_hash=get_user_data["password_hash"],
        role=UserRole.USER,
        is_verified=True,
        is_active=True,
    )


@pytest.fixture(scope="session")
def get_token_life_time() -> dict:
    active_time = datetime.utcnow() + timedelta(minutes=30)
    inactive_time = datetime.utcnow() - timedelta(minutes=30)
    return {
        "active_time": active_time,
        "inactive_time": inactive_time,
    }


@pytest.fixture
def valid_user_creation_data(
    get_user_data,
) -> CreateUserExtendedScheme:
    return CreateUserExtendedScheme(
        email=get_user_data["email"],
        password_hash=get_user_data["password_hash"],
        role=RoleEnum.USER,
    )


@pytest.fixture
def invalid_admin_creation_data(
    get_user_data,
) -> CreateUserExtendedScheme:
    return CreateUserExtendedScheme(
        email=get_user_data["email"],
        password_hash=get_user_data["password_hash"],
        role=RoleEnum.ADMIN,
        admin_code=None,
    )


@pytest.fixture
def refresh_user_payload(
    get_token_life_time,
    get_user_data,
    user_id,
) -> dict:
    return {
        "user_id": str(user_id),
        "email": get_user_data["email"],
        "role": UserRole.USER,
        "expires": get_token_life_time["active_time"],
        "token_type": "refresh",
    }


@pytest.fixture
def mock_ses_handler(
    verification_code
):
    with patch.object(ses_handler, "generate_email_payload") as mock_gen_payload, \
        patch.object(ses_handler, "send_email", new_callable=AsyncMock) as mock_send_email, \
        patch.object(ses_handler, "generate_otp") as mock_generate_otp:
        # patch.object(ses_handler, "reset_password", new_callable=AsyncMock) as mock_reset_pwd:
        mock_send_email.return_value = None
        # mock_reset_pwd.return_value =
        mock_generate_otp.return_value = verification_code
        mock_gen_payload.return_value = EmailPayloadScheme(
            message="Test message",
            subject="Test subject",
            source="sender@example.com",
        )

        yield {
            "mock_send_email": mock_send_email,
            "mock_generate_otp": mock_generate_otp,
            "mock_gen_payload": mock_gen_payload,
        }


@pytest.fixture
def mock_message_creator(mocker):
    mock_msg = mocker.patch(
        "auth_app.services.users.msg_creator.get_code_message",
        return_value="Code sent",
    )
    return mock_msg
