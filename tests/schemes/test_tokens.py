from datetime import datetime

import pytest
from pydantic import ValidationError

from auth_app.schemes.tokens import (
    CreateDataScheme,
    CreateRefreshScheme,
    DeleteRefreshScheme,
    GetRefreshScheme,
)
from auth_app.schemes.users import RoleEnum


def test_create_data() -> None:
    valid_data = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "mail@example.com",
        "role": RoleEnum.ADMIN,
        "admin_secret": "123secret",
    }
    valid_data_case = CreateDataScheme.model_validate(valid_data)
    assert valid_data_case.email == "mail@example.com"
    assert valid_data_case.role == "ADMIN"
    assert valid_data_case.admin_secret == "123secret"

    invalid_data = {
        "user_id": 1,
        "email": "email",
        "role": "UNSET",
        "admin_secret": {'qwe': 'qwe'},
    }
    with pytest.raises(ValidationError):
        CreateDataScheme.model_validate(invalid_data)

    extra_fields = {
        "abc": "abc",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "mail@example.com",
        "role": RoleEnum.ADMIN,
        "admin_secret": "123secret",
    }
    extra_fields_case = CreateDataScheme.model_validate(extra_fields)
    assert extra_fields_case.role == "ADMIN"
    assert extra_fields_case.email == "mail@example.com"
    assert extra_fields_case.admin_secret == "123secret"

    partial_data = {
        "email": "mail@example.com",
    }
    with pytest.raises(ValidationError):
        CreateDataScheme.model_validate(partial_data)


def test_create_refresh() -> None:
    valid_data = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...",
        "expires_at": "2025-01-01T15:34:00",
    }
    valid_data_case = CreateRefreshScheme.model_validate(valid_data)
    assert str(valid_data_case.user_id) == "123e4567-e89b-12d3-a456-426614174000"
    assert valid_data_case.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."
    assert isinstance(valid_data_case.expires_at, datetime)

    invalid_data = {
        "user_id": 123,
        "token": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."],
        "expires_at": "xyz",
    }
    with pytest.raises(ValidationError):
        CreateRefreshScheme.model_validate(invalid_data)

    extra_fields = {
        "abc": "abc",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...",
        "expires_at": "2025-01-01T15:34:00",
    }
    extra_fields_case = CreateRefreshScheme.model_validate(extra_fields)
    assert extra_fields_case.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."
    assert str(extra_fields_case.user_id) == "123e4567-e89b-12d3-a456-426614174000"

    partial_data = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
    }
    with pytest.raises(ValidationError):
        CreateRefreshScheme.model_validate(partial_data)


def test_get_refresh() -> None:
    valid_data = {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...",
        "expires_at": "2025-01-01T15:34:00",
    }
    valid_data_case = GetRefreshScheme.model_validate(valid_data)
    assert str(valid_data_case.id) == "123e4567-e89b-12d3-a456-426614174001"
    assert str(valid_data_case.user_id) == "123e4567-e89b-12d3-a456-426614174000"
    assert valid_data_case.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."
    assert isinstance(valid_data_case.expires_at, datetime)

    invalid_data = {
        "id": 1,
        "user_id": 2,
        "token": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."],
        "expires_at": 4,
    }
    with pytest.raises(ValidationError):
        GetRefreshScheme.model_validate(invalid_data)

    extra_fields = {
        "abc": "abc",
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...",
        "expires_at": "2025-01-01T15:34:00",
    }
    extra_fields_case = GetRefreshScheme.model_validate(extra_fields)
    assert str(extra_fields_case.id) == "123e4567-e89b-12d3-a456-426614174001"
    assert str(extra_fields_case.user_id) == "123e4567-e89b-12d3-a456-426614174000"
    assert extra_fields_case.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."
    assert isinstance(extra_fields_case.expires_at, datetime)

    partial_data = {
        "id": "123e4567-e89b-12d3-a456-426614174001",
    }
    with pytest.raises(ValidationError):
        GetRefreshScheme.model_validate(partial_data)


def test_delete_refresh() -> None:
    valid_data = {
        "email": "mail@example.com",
        "password_hash": "test_password",
    }

    valid_data_case = DeleteRefreshScheme.model_validate(valid_data)
    assert isinstance(valid_data_case.password_hash, str)
    assert isinstance(valid_data_case.email, str)
    assert valid_data_case.email == "mail@example.com"
    assert valid_data_case.password_hash == "test_password"

    extra_fields = {
        "abc": "abc",
        "email": "mail@example.com",
        "password_hash": "test_password",
    }
    extra_fields_case = DeleteRefreshScheme.model_validate(extra_fields)
    assert extra_fields_case.email == "mail@example.com"
    assert extra_fields_case.password_hash == "test_password"

    partial_data = {
        "email": "mail@example.com",
    }
    with pytest.raises(ValidationError):
        DeleteRefreshScheme.model_validate(partial_data)

    no_data = {
    }
    with pytest.raises(ValidationError):
        DeleteRefreshScheme.model_validate(no_data)

    wrong_data = {
        "email": 123,
        "password_hash": 123,
    }
    with pytest.raises(ValidationError):
        DeleteRefreshScheme.model_validate(wrong_data)
