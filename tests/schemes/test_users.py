import pytest
from pydantic import ValidationError

from auth_app.schemes.users import (
    AuthUserScheme,
    CreateResponseScheme,
    CreateUserScheme,
    DeleteUserScheme,
    GetUserScheme,
    MessageResponseScheme,
    PatchUserScheme,
    PutUserScheme,
    RoleEnum,
    UserFilterScheme,
    VerificationScheme,
    client_roles,
    stuffer_roles,
)


def test_role_enum() -> None:
    assert RoleEnum.USER == "USER"
    assert RoleEnum.ADMIN == "ADMIN"
    assert RoleEnum.STAFFER == "STAFFER"
    assert RoleEnum.OTHER == "OTHER"
    assert RoleEnum.USER in client_roles
    assert RoleEnum.USER not in stuffer_roles
    assert isinstance(client_roles, list)
    assert isinstance(stuffer_roles, list)


def test_auth_user_data() -> None:
    valid_data = {
        "email": "email@example.com",
        "password_hash": "password_example_123",
    }
    invalid_email = {
        "email": 1234,
        "password_hash": "password_example_123",
    }
    invalid_password = {
        "email": "email@example.com",
        "password_hash": "123",
    }

    valid_case = AuthUserScheme(**valid_data)
    assert valid_case.email == "email@example.com"
    assert valid_case.password_hash == "password_example_123"

    with pytest.raises(ValidationError):
        AuthUserScheme(**invalid_email)

    with pytest.raises(ValidationError):
        AuthUserScheme(**invalid_password)


def test_auth_create_user() -> None:
    valid_data = {
        "email": "email@example.com",
        "password_hash": "password_example_123",
        "role": "USER",
    }
    invalid_data = {
        "email": "email@example.com",
        "password_hash": "password_example_123",
        "role": "UNSET_ROLE",
    }

    valid_data_case = CreateUserScheme(**valid_data)
    assert valid_data_case.role == "USER"

    with pytest.raises(ValidationError):
        CreateUserScheme(**invalid_data)


def test_message_response() -> None:
    valid_data = {
        "message": "some message",
    }
    invalid_data = {
        "message": {
            "key": "value",
        }
    }

    valid_data_case = MessageResponseScheme.model_validate(valid_data)
    assert valid_data_case.message == "some message"

    with pytest.raises(ValidationError):
        MessageResponseScheme.model_validate(invalid_data)


def test_get_user() -> None:
    valid_data = {
        "email": "email@example.com",
        "password_hash": "password_example_123",
        "id": "150881a3-c874-4a93-92d2-6be10a4c189c",
        "role": RoleEnum.USER,
        "is_verified": False,
        "is_active": True,
    }
    no_fields_data = {
        "email": "email@example.com",
        "password_hash": "password_example_123",
    }
    extra_fields_data = {
        "abc": "abc",
        "email": "email@example.com",
        "password_hash": "password_example_123",
        "id": "150881a3-c874-4a93-92d2-6be10a4c189c",
        "role": RoleEnum.USER,
        "is_verified": False,
        "is_active": True,
    }
    wrong_type_data = {
        "email": "email@example.com",
        "password_hash": "password_example_123",
        "id": 123,
        "role": RoleEnum.USER,
        "is_verified": "False",
        "is_active": "True",
    }

    valid_data_case = GetUserScheme.model_validate(valid_data)
    assert valid_data_case.role == "USER"
    assert "150881a3" in str(valid_data_case.id)
    assert valid_data_case.is_active
    assert not valid_data_case.is_verified

    extra_fields_case = GetUserScheme.model_validate(extra_fields_data)
    assert extra_fields_case.role == "USER"
    assert "150881a3" in str(extra_fields_case.id)

    with pytest.raises(ValidationError):
        GetUserScheme.model_validate(no_fields_data)

    with pytest.raises(ValidationError):
        GetUserScheme.model_validate(wrong_type_data)


def test_create_response() -> None:
    user_data = {
        "email": "email@example.com",
        "password_hash": "password_example_123",
        "id": "150881a3-c874-4a93-92d2-6be10a4c189c",
        "role": RoleEnum.USER,
        "is_verified": False,
        "is_active": True,
    }
    get_user = GetUserScheme.model_validate(user_data)
    valid_data = {
        "message": "some message",
        "record": get_user,
    }

    valid_data_case = CreateResponseScheme.model_validate(valid_data)
    assert isinstance(valid_data_case.record, GetUserScheme)
    assert isinstance(valid_data_case.message, str)
    assert valid_data_case.record.role == "USER"
    assert valid_data_case.record.is_active
    assert valid_data_case.message == "some message"


def test_patch_user() -> None:
    all_fields = {
        "email": "email@example.com",
        "password_hash": "new_password_12345",
        "is_verified": False,
        "is_active": True,
    }
    partial_fields = {
        "password_hash": "new_password_12345",
    }
    invalid_types = {
        "email": 1234,
        "password_hash": [123, 321],
        "is_verified": "False",
        "is_active": "True",
    }
    extra_fields = {
        "abc": "abc",
        "email": "email@example.com",
        "password_hash": "new_password_12345",
        "is_verified": False,
        "is_active": True,
    }

    all_fields_case = PatchUserScheme.model_validate(all_fields)
    assert all_fields_case.email == "email@example.com"
    assert all_fields_case.password_hash == "new_password_12345"
    assert all_fields_case.is_active
    assert not all_fields_case.is_verified

    partial_fields_case = PatchUserScheme.model_validate(partial_fields)
    assert partial_fields_case.password_hash == "new_password_12345"
    assert partial_fields_case.email is None

    extra_fields_case = PatchUserScheme.model_validate(extra_fields)
    assert extra_fields_case.email == "email@example.com"
    assert extra_fields_case.password_hash == "new_password_12345"

    with pytest.raises(ValidationError):
        PatchUserScheme(**invalid_types)


def test_put_user() -> None:
    all_fields = {
        "email": "email@example.com",
        "password_hash": "new_password_12345",
        "is_verified": False,
        "is_active": True,
    }
    partial_fields = {
        "password_hash": "new_password_12345",
    }
    invalid_types = {
        "email": 1234,
        "password_hash": [123, 321],
        "is_verified": "False",
        "is_active": "True",
    }
    extra_fields = {
        "abc": "abc",
        "email": "email@example.com",
        "password_hash": "new_password_12345",
        "is_verified": False,
        "is_active": True,
    }

    all_fields_case = PutUserScheme.model_validate(all_fields)
    assert all_fields_case.email == "email@example.com"
    assert all_fields_case.password_hash == "new_password_12345"
    assert all_fields_case.is_active
    assert not all_fields_case.is_verified

    extra_fields = PutUserScheme.model_validate(extra_fields)
    assert extra_fields.email == "email@example.com"
    assert extra_fields.password_hash == "new_password_12345"

    with pytest.raises(ValidationError):
        PutUserScheme.model_validate(partial_fields)

    with pytest.raises(ValidationError):
        PutUserScheme.model_validate(invalid_types)


def test_delete_user() -> None:
    all_fields = {
        "email": "email@example.com",
        "password_hash": "password_12345",
        "id": "150881a3-c874-4a93-92d2-6be10a4c189c",
    }
    partial_fields = {
        "email": "email@example.com",
        "password_hash": "password_12345",
    }
    no_fields = {
        "id": "150881a3-c874-4a93-92d2-6be10a4c189c",
    }
    wrong_type_fields = {
        "email": 123,
        "password_hash": ['123', 123],
        "id": 123,
    }

    all_fields_case = DeleteUserScheme.model_validate(all_fields)
    assert all_fields_case.email == "email@example.com"
    assert all_fields_case.password_hash == "password_12345"
    assert "150881a3" in str(all_fields_case.id)

    partial_fields_case = DeleteUserScheme.model_validate(partial_fields)
    assert partial_fields_case.id is None
    assert all_fields_case.email == "email@example.com"
    assert all_fields_case.password_hash == "password_12345"

    with pytest.raises(ValidationError):
        DeleteUserScheme.model_validate(wrong_type_fields)

    with pytest.raises(ValidationError):
        DeleteUserScheme.model_validate(no_fields)

    with pytest.raises(ValidationError):
        DeleteUserScheme.model_validate(no_fields)


def test_user_filter() -> None:
    all_fields = {
        "id": "150881a3-c874-4a93-92d2-6be10a4c189c",
        "email": "email@example.com",
        "role": RoleEnum.USER,
        "is_verified": False,
        "is_active": True,
    }
    partial_fields = {
        "role": RoleEnum.USER,
        "is_verified": False,
    }
    no_fields = {
    }
    extra_fields = {
        "abc": "abc",
        "id": "150881a3-c874-4a93-92d2-6be10a4c189c",
        "email": "email@example.com",
        "role": RoleEnum.USER,
        "is_verified": False,
        "is_active": True,
    }
    wrong_type = {
        "id": 123,
        "email": 123,
        "role": 123,
        "is_verified": "False",
        "is_active": "True",
    }

    all_fields_case = UserFilterScheme.model_validate(all_fields)
    assert all_fields_case.email == "email@example.com"
    assert all_fields_case.role == "USER"
    assert all_fields_case.is_active

    partial_fields_case = UserFilterScheme.model_validate(partial_fields)
    assert partial_fields_case.role == "USER"
    assert partial_fields_case.email is None

    no_fields_case = UserFilterScheme.model_validate(no_fields)
    assert no_fields_case.email is None
    assert no_fields_case.role is None
    assert no_fields_case.id is None

    extra_fields_case = UserFilterScheme.model_validate(extra_fields)
    assert extra_fields_case.email == "email@example.com"
    assert extra_fields_case.role == "USER"
    assert extra_fields_case.is_active

    with pytest.raises(ValidationError):
        UserFilterScheme.model_validate(wrong_type)


def test_verification_data() -> None:
    valid_data = {
        "email": "email@example.com",
        "verification_code": "123Qwe!",
    }
    invalid_type = {
        "email": 123,
        "verification_code": 123,
    }
    extra_fields = {
        "abc": "abc",
        "email": "email@example.com",
        "verification_code": "123Qwe!",
    }
    no_fields = {
    }

    valid_data_case = VerificationScheme.model_validate(valid_data)
    assert valid_data_case.email == "email@example.com"
    assert isinstance(valid_data_case.verification_code, str)
    assert valid_data_case.verification_code == "123Qwe!"

    extra_fields_case = VerificationScheme.model_validate(extra_fields)
    assert extra_fields_case.email == "email@example.com"
    assert isinstance(extra_fields_case.verification_code, str)
    assert extra_fields_case.verification_code == "123Qwe!"

    with pytest.raises(ValidationError):
        VerificationScheme.model_validate(invalid_type)

    with pytest.raises(ValidationError):
        VerificationScheme.model_validate(no_fields)
