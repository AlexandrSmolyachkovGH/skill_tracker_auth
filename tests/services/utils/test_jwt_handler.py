from auth_app.schemes.tokens import CreateDataScheme
from auth_app.services.utils.jwt_handler import JWTHandler

jwt_handler = JWTHandler()


def test_get_refresh_response(
    refresh_tokens_mock: dict,
) -> None:
    """
    Test that get_refresh_response returns correct response
    """
    token = refresh_tokens_mock["user_refresh_mock"]
    payload = refresh_tokens_mock["user_payload_mock"]
    response = JWTHandler.get_refresh_response(
        token=token,
        payload=payload,
    )

    assert isinstance(response, dict)
    assert response["refresh_token"] == token
    assert response["payload"] == payload


def test_get_access_response(
    access_token_mock: dict,
) -> None:
    """
    Test that get_access_response returns correct response
    """
    access_token = access_token_mock["access_token"]
    response = JWTHandler.get_access_response(
        token=access_token,
    )
    assert isinstance(response, dict)
    assert response["access_token"] == access_token


def test_generate_refresh(
    create_user_data: CreateDataScheme,
) -> None:
    """
    Test creation of refresh token
    """
    refresh_response = jwt_handler.generate_refresh(
        create_data=create_user_data,
    )

    assert isinstance(refresh_response, dict)
    assert isinstance(refresh_response["refresh_token"], str)
    assert isinstance(refresh_response["payload"], dict)
    assert refresh_response["payload"]["email"] == create_user_data.email


def test_generate_access(
    refresh_tokens_mock: dict,
) -> None:
    """
    Test creation of access token
    """
    token = refresh_tokens_mock["user_refresh_mock"]
    access_response = jwt_handler.generate_access(
        refresh_token=token,
        extra_payload={},
    )
    assert isinstance(access_response, dict)
    assert isinstance(access_response["access_token"], str)


def test_base_decode(
    refresh_tokens_mock: dict,
) -> None:
    """
    Test successful decoding of the token
    """
    token = refresh_tokens_mock["user_refresh_mock"]
    refresh_payload = JWTHandler.base_decode(token)

    assert isinstance(refresh_payload, dict)
    assert refresh_payload["token_type"] == "refresh"
