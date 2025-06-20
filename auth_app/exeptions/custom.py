class AttrError(ValueError):
    pass


class ServiceError(Exception):
    """Base class for service-level business errors."""


class TokenError(Exception):
    """Base class for token related errors."""


class UserVerificationError(ValueError, ServiceError):
    """
    Error with verification
    """

    def __init__(self) -> None:
        message = "The user is not verified or verification failed"
        super().__init__(message)


class UserActivityError(ValueError):
    """
    Error in activity status of user
    """

    def __init__(self) -> None:
        message = "The user's record must be active"
        super().__init__(message)
