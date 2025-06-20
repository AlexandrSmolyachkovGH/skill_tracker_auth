import pytest
from pydantic import ValidationError

from auth_app.schemes.email import EmailPayloadScheme


def test_email_payload() -> None:
    all_fields = {
        "message": "Test message",
        "subject": "Test subject",
        "source": "sender@example.com",
    }

    all_fields_case = EmailPayloadScheme.model_validate(all_fields)
    assert isinstance(all_fields_case.message, str)
    assert all_fields_case.message == "Test message"
    assert isinstance(all_fields_case.subject, str)
    assert all_fields_case.subject == "Test subject"
    assert isinstance(all_fields_case.source, str)
    assert all_fields_case.source == "sender@example.com"

    partial_fields = {
        "message": "Test message",
        "subject": "Test subject",
    }
    partial_fields_case = EmailPayloadScheme.model_validate(partial_fields)
    assert partial_fields_case.message == "Test message"
    assert partial_fields_case.source == "sender@example.com"

    extra_fields = {
        "abc": "abc",
        "message": "Test message",
        "subject": "Test subject",
        "source": "sender@example.com",
    }
    extra_fields_case = EmailPayloadScheme.model_validate(extra_fields)
    assert extra_fields_case.message == "Test message"
    assert extra_fields_case.source == "sender@example.com"

    wrong_types = {
        "message": ["Test message", 123],
        "subject": True,
        "source": 123,
    }

    with pytest.raises(ValidationError):
        EmailPayloadScheme.model_validate(wrong_types)
