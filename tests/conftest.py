from datetime import (
    datetime,
    timedelta,
)
from unittest.mock import (
    AsyncMock,
    MagicMock,
    Mock,
)
from uuid import (
    UUID,
    uuid4,
)

import pytest
from aiobotocore.client import AioBaseClient
from redis.asyncio.client import Redis

from auth_app.config import jwt_settings
from auth_app.models import (
    RefreshTokenORM,
    UserORM,
)
from auth_app.models.users import UserRole
from auth_app.schemes.tokens import CreateDataScheme
from auth_app.schemes.users import (
    CreateUserExtendedScheme,
    GetUserScheme,
    RoleEnum,
)
from auth_app.services.tokens import TokenService
from auth_app.services.users import UserService
from auth_app.services.utils.pwd_hashing import hash_password
from auth_app.services.utils.token_handler import token_handler


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
def mock_dependencies() -> dict:
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
        "ses": Mock(

        ),
    }


@pytest.fixture
def mock_user_repo() -> MagicMock:
    return MagicMock(
        create_user=AsyncMock(),
        get_user=AsyncMock(),
        update_user=AsyncMock(),
        get_users=AsyncMock(),
    )


@pytest.fixture
def mock_token_repo() -> MagicMock:
    return MagicMock(
        create_refresh=AsyncMock(),
        get_refresh=AsyncMock(),
        update_refresh=AsyncMock(),
    )


@pytest.fixture
def verification_code() -> str:
    return "123Code!"


@pytest.fixture
def mock_redis(
    verification_code,
) -> MagicMock:
    mock = MagicMock(spec=Redis)
    mock.set = AsyncMock(return_value=None)
    mock.get = AsyncMock(return_value=verification_code)
    return mock


@pytest.fixture
def mock_ses() -> MagicMock:
    return MagicMock(spec=AioBaseClient)


@pytest.fixture
def mock_user_service(
    mock_user_repo,
    mock_token_repo,
    mock_redis,
    mock_ses,
) -> UserService:
    return UserService(
        user_repo=mock_user_repo,
        token_repo=mock_token_repo,
        redis=mock_redis,
        ses=mock_ses,
    )


@pytest.fixture
def mock_token_service(
    mock_user_repo,
    mock_token_repo,
    mock_redis,
    mock_ses,
) -> TokenService:
    return TokenService(
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
def user_id() -> UUID:
    return uuid4()


@pytest.fixture(scope="session")
def user_orm_mock(
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
def verified_user_orm_mock(
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
def token_life_time_mock() -> dict:
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
    token_life_time_mock,
    get_user_data,
    user_id,
) -> dict:
    return {
        "user_id": str(user_id),
        "email": get_user_data["email"],
        "role": UserRole.USER,
        "expires": token_life_time_mock["active_time"],
        "token_type": "refresh",
    }


@pytest.fixture
def mock_message_creator(
    mocker,
) -> MagicMock:
    mock_msg = mocker.patch(
        "auth_app.services.users.msg_creator.get_code_message",
        return_value="Code sent",
    )
    return mock_msg


@pytest.fixture(scope="session")
def create_user_data(
    user_orm_mock: UserORM,
) -> CreateDataScheme:
    return CreateDataScheme(
        user_id=user_orm_mock.id,
        email=user_orm_mock.email,
        role=RoleEnum.USER,
        admin_secret=None,
    )


@pytest.fixture(scope="session")
def create_admin_data(
    user_orm_mock: UserORM,
) -> CreateDataScheme:
    return CreateDataScheme(
        user_id=user_orm_mock.id,
        email=user_orm_mock.email,
        role=RoleEnum.ADMIN,
        admin_secret=jwt_settings.ADMIN_SECRET.get_secret_value(),
    )


@pytest.fixture(scope="session")
def refresh_tokens_mock(
    create_user_data: CreateDataScheme,
    create_admin_data: CreateDataScheme,
) -> dict:
    user_refresh_mock = token_handler.generate_refresh(
        create_user_data,

    )
    admin_refresh_mock = token_handler.generate_refresh(
        create_admin_data,
    )
    return {
        "user_refresh_mock": user_refresh_mock["refresh_token"],
        "user_payload_mock": user_refresh_mock["payload"],
        "admin_refresh_mock": admin_refresh_mock["refresh_token"],
        "admin_payload_mock": admin_refresh_mock["payload"],
    }


@pytest.fixture(scope="session")
def access_token_mock(
    refresh_tokens_mock,
) -> dict:
    access_token = token_handler.generate_access(
        refresh_token=refresh_tokens_mock["user_refresh_mock"],
        extra_payload={},
    )
    return access_token


@pytest.fixture(scope="session")
def refresh_orm_mock(
    refresh_tokens_mock,
) -> RefreshTokenORM:
    payload = refresh_tokens_mock["user_payload_mock"]

    refresh_orm = RefreshTokenORM(
        id=uuid4(),
        user_id=payload["user_id"],
        token=refresh_tokens_mock["user_refresh_mock"],
        expires_at=payload["expires"],
    )
    return refresh_orm


@pytest.fixture(scope="session")
def get_user_scheme_mock(
    user_orm_mock,
) -> GetUserScheme:
    return GetUserScheme(
        email=user_orm_mock.email,
        password_hash=user_orm_mock.password_hash,
        id=user_orm_mock.id,
        role=user_orm_mock.role,
        is_verified=user_orm_mock.is_verified,
        is_active=user_orm_mock.is_active,
    )
