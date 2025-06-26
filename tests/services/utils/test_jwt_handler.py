from uuid import UUID

from auth_app.schemes.tokens import CreateDataScheme
from auth_app.schemes.users import RoleEnum
from auth_app.services.utils.jwt_handler import JWTHandler

jwt_handler = JWTHandler()
create_data = CreateDataScheme(
    user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    email="mail@example.com",
    role=RoleEnum.USER,
)
extra_payload = {
    "test": "test",
}
token = jwt_handler.generate_refresh(create_data=create_data)["refresh_token"]
access_token = jwt_handler.generate_access(
    refresh_token=token,
    extra_payload=extra_payload,
)["access_token"]
payload = jwt_handler.base_decode(token)
access_payload = jwt_handler.base_decode(access_token)


def test_get_refresh_response() -> None:
    response = JWTHandler.get_refresh_response(
        token=token,
        payload=payload,
    )
    assert isinstance(response, dict)
    assert response["refresh_token"] == token
    assert response["payload"] == payload


def test_get_access_response() -> None:
    response = JWTHandler.get_access_response(
        token=access_token,
    )
    assert response["access_token"] == access_token
    assert isinstance(response, dict)


def test_generate_refresh() -> None:
    refresh_response = jwt_handler.generate_refresh(
        create_data=create_data,
    )
    assert isinstance(refresh_response, dict)
    assert isinstance(refresh_response["refresh_token"], str)
    assert isinstance(refresh_response["payload"], dict)
    assert refresh_response["payload"]["email"] == "mail@example.com"


def test_generate_access() -> None:
    access_response = jwt_handler.generate_access(
        refresh_token=token,
        extra_payload=extra_payload,
    )
    assert isinstance(access_response, dict)
    assert isinstance(access_response["access_token"], str)


def test_base_decode() -> None:
    refresh_payload = JWTHandler.base_decode(token)
    assert isinstance(refresh_payload, dict)
    assert refresh_payload["token_type"] == "refresh"
