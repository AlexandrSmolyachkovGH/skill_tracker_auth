from auth_app.messages.common import msg_creator


def test_messages() -> None:
    """
    Test of expected answers of the msg_creator
    """

    assert msg_creator.get_code_message("123") == f"Your verification code was sent to 123."
    assert msg_creator.get_reset_pwd_message() == "Password was changed. Check your email to get it."
    assert msg_creator.get_root_description() == "Auth REST API for the Skill Tracker Application"
    assert msg_creator.get_root_title() == "Skill Tracker Auth Service"
    ses_reset_pwd_msg = msg_creator.get_ses_reset_pwd_message("123456")
    assert isinstance(ses_reset_pwd_msg, dict)
    assert ses_reset_pwd_msg["subject"] == "Auth service: Password reset"
    ses_confirmation_message = msg_creator.get_ses_confirmation_message("12345")
    assert isinstance(ses_confirmation_message, dict)
    assert ses_confirmation_message["subject"] == "Auth service: Verification code"
