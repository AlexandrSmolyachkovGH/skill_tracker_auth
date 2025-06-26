class MessageCreator:
    """
    General class for creating text messages and responses.
    """

    @staticmethod
    def get_code_message(email: str) -> str:
        message = f"Your verification code was sent to {email}."
        return message

    @staticmethod
    def get_reset_pwd_message() -> str:
        return "Password was changed. Check your email to get it."

    @staticmethod
    def get_root_description() -> str:
        return "Auth REST API for the Skill Tracker Application"

    @staticmethod
    def get_root_title() -> str:
        return "Skill Tracker Auth Service"

    @staticmethod
    def get_ses_reset_pwd_message(password: str) -> dict:
        message = f"Your new password: {password}"
        subject = "Auth service: Password reset"
        return {
            "message": message,
            "subject": subject,
        }

    @staticmethod
    def get_ses_confirmation_message(code: str) -> dict:
        message = (
            f"Your verification code is: {code}\n"
            f"This code will be active only for 5 minutes."
        )
        subject = "Auth service: Verification code"
        response = "Verification code was sent. Check your email to get it."
        return {
            "message": message,
            "subject": subject,
            "response_message": response,
        }


msg_creator = MessageCreator()
